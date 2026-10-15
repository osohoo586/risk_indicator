"""python ri.py <command> ...   (python ri.py -h)

Сонголт (run, verify, auto, clean): файл эсвэл folder-ийн зам, -i RI_ID, -a BRANCHID|ACT_NN, --all
    python ri.py run --env local activities/act_01_corporate_business/ -p 2026-Q3
    python ri.py run --env local activities/act_40_human_resources/ri_40_1520.sql -d 2026-09-30
    python ri.py run --env local activities/_shared/sh_007.sql -p 2026-Q3     # тооцооллыг ашигладаг бүх үзүүлэлт
Хугацаа: -p 2026-Q3 (олон удаа, эхлэл + төгсгөл), -d 2026-09-30 (эхлэл нь frequency/period-оос),
    --from/--to (давтамжийн огноонуудаар backfill), эсвэл config/period.yaml.
"""
import argparse
import datetime as dt
import logging
import sys
from pathlib import Path

from . import manual, orgmap, progress, scaffold, store, tools
from .checks import run_checks
from .config import ACTIVITIES_DIR, ENVIRONMENTS, LOGS_DIR, ConfigError, EnvConfig, load_period
from .dates import date_range, is_due, parse_date, parse_period, to_date
from .db import connect
from .metadata import (CALC_FILE_RE, FREQUENCIES, INDICATOR_FILE_RE, SHARED_DIR as CALC_DIR, Catalog,
                       apply_env_params, load_catalog)
from .runner import RunContext, has_problems, print_activity_scores, refresh_activities, run_plan, select


def _setup_logging(run_id: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if run_id:
        folder = LOGS_DIR / f"{dt.date.today():%Y-%m-%d}"
        folder.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(folder / f"{run_id}.log", encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s",
                        datefmt="%H:%M:%S", handlers=handlers, force=True)


def _dates(args) -> list[dt.date]:
    if getattr(args, "date", None):
        return [parse_date(args.date)]
    if getattr(args, "period", None):
        return sorted({parse_period(x)[1] for x in args.period})
    if getattr(args, "date_from", None) and getattr(args, "date_to", None):
        return date_range(parse_date(args.date_from), parse_date(args.date_to))
    return []


def ids_from_paths(cat: Catalog, paths) -> list[str]:
    """Файл / folder-ийн зам → үзүүлэлтийн ID-ууд.

    ri_GG_NNNN.sql → тэр үзүүлэлт; activities/_shared/sh_NNN.sql → тодорхойлолтыг ашигладаг бүх үзүүлэлт;
    act_GG_*/activity.yaml → тэр үйл ажиллагааны нийтлэг тодорхойлолтын мөрүүд (shared:);
    folder → доторх бүх үзүүлэлт (activities/ = бүгд, activities/_shared/ = бүх нийтлэг тодорхойлолтын хэрэглэгч)."""
    ids: list[str] = []
    for raw in paths or []:
        p = Path(raw).resolve()
        if p.is_file():
            if CALC_FILE_RE.match(p.name):
                users = sorted(i.indicator_id for i in cat.indicators.values()
                               if (i.calc or i.def_id) == p.stem.upper())
                if not users:
                    raise ValueError(f"{raw}: {p.stem.upper()}-ийг ашигладаг үзүүлэлт алга")
                ids += users
                continue
            if p.name == "activity.yaml":
                rows = sorted(i.indicator_id for i in cat.indicators.values()
                              if i.manifest is not None and Path(i.folder).resolve() == p.parent)
                if not rows:
                    raise ValueError(f"{raw}: shared: мөр алга")
                ids += rows
                continue
            ind = cat.indicators.get(p.stem.upper()) if INDICATOR_FILE_RE.match(p.name) else None
            if ind is None or ind.file_path.resolve() != p:
                raise ValueError(f"{raw}: activities/act_GG_*/ri_GG_NNNN.sql биш эсвэл тохиргоо нь алдаатай "
                                 f"(python ri.py check)")
            ids.append(ind.indicator_id)
        elif p.is_dir():
            if p == (ACTIVITIES_DIR / CALC_DIR).resolve():
                found = sorted(i.indicator_id for i in cat.indicators.values() if i.mode == "shared")
            else:
                found = sorted(i.indicator_id for i in cat.indicators.values()
                               if p == i.folder.resolve() or p in i.folder.resolve().parents)
            if not found:
                raise ValueError(f"{raw}: дотор нь үзүүлэлт алга")
            ids += found
        else:
            raise ValueError(f"{raw}: зам олдсонгүй")
    return list(dict.fromkeys(ids))


def _add_selection(p, required_date=True):
    p.add_argument("paths", nargs="*", help="Файл эсвэл folder: activities/act_01_corporate_business/ri_01_0002.sql")
    p.add_argument("--env", required=True, choices=ENVIRONMENTS)
    p.add_argument("--indicator", "-i", action="append", help="RI_01_0002 (олон удаа өгч болно)")
    p.add_argument("--activity", "-a", action="append", help="BRANCHID (998) эсвэл ACT_01 (олон удаа)")
    p.add_argument("--all", action="store_true", help="Бүх үзүүлэлт (жишээ activity-аас бусад)")
    if required_date:
        p.add_argument("--date", "-d", help="Тайлант огноо YYYY-MM-DD")
        p.add_argument("--period", "-p", action="append", help="Тайлант хугацаа: 2026-Q3, 2026-H1, 2026-09, 2026")
        p.add_argument("--from", dest="date_from", help="Эхлэх огноо (backfill)")
        p.add_argument("--to", dest="date_to", help="Дуусах огноо (backfill)")


def _selected_ids(cat: Catalog, args) -> list[str]:
    return [i.upper() for i in (args.indicator or [])] + ids_from_paths(cat, getattr(args, "paths", None))


# ── Commands ──────────────────────────────────────────────────────────────────
def cmd_check(args) -> int:
    if getattr(args, "env", None):
        _, cat = _env(args.env)
    else:
        cat = load_catalog()
    ids = None
    if args.indicator or args.activity or getattr(args, "paths", None):
        ids = _selected_ids(cat, args)
        for a in args.activity or []:
            ids += [x.indicator_id for x in cat.by_branch(a)]
        ids = [i for i in dict.fromkeys(ids) if i in cat.indicators]
    errors, warnings = run_checks(cat, ids)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    n = len(ids) if ids is not None else len(cat.indicators)
    print(f"\n{n} үзүүлэлт шалгав: {len(errors)} алдаа, {len(warnings)} анхааруулга")
    return 1 if errors else 0


def cmd_init_db(args) -> int:
    cfg = EnvConfig(args.env)
    with connect(cfg, cfg.result_connection) as conn:
        created = store.ensure_base(cfg, conn)
        store.ensure_views(cfg, conn)
    print(f"{cfg.result_db}.{store.RESULT_TABLE}, {store.ACTIVITY_TABLE}, {store.INDICATOR_TABLE}, "
          f"{store.AUDIT_TABLE}, {store.HISTORY_TABLE} " + ("үүсгэлээ." if created else "бэлэн байна."))
    print(f"View (UI): {', '.join(store.VIEWS)}")
    orgmap.use(cfg)
    from .runner import sync_meta
    sync_meta(cfg, load_catalog())
    return 0


def _env(env: str):
    """Орчны config + түүний org mapping-ээр catalog (+ config params)."""
    cfg = EnvConfig(env)
    orgmap.use(cfg)
    cat = load_catalog()
    apply_env_params(cat, cfg)
    return cfg, cat


def _select(cat, cfg, args):
    if not (args.indicator or args.activity or args.all or getattr(args, "paths", None)):
        raise ValueError("Файл / folder-ийн зам, --indicator, --activity эсвэл --all-ийн аль нэгийг өгнө үү")
    return select(cat, cfg, _selected_ids(cat, args), args.activity, args.all,
                  getattr(args, "frequency", None), getattr(args, "with_deps", False))


def cmd_run(args) -> int:
    cfg, cat = _env(args.env)
    for err in cat.errors:
        print(f"METADATA АЛДАА (ажиллахгүй): {err}")
    runnable, skipped = _select(cat, cfg, args)
    period_start = None
    period_starts: dict = {}
    if args.period:                         # -p 2026-Q3: эхлэл + төгсгөл шууд → frequency шалгахгүй
        for x in args.period:
            start, end = parse_period(x)
            period_starts[end] = start
        args.force = True
    if args.test_dates:
        plan: dict[dt.date, list] = {}
        for ind in runnable:
            if not ind.test_dates:
                print(f"{ind.indicator_id}: test_dates хоосон — алгаслаа")
            for d in ind.test_dates:
                plan.setdefault(d, []).append(ind)
    else:
        dates = _dates(args)
        if not dates:
            per = load_period()
            if per.get("end_date"):
                period_end = to_date(per["end_date"])
                period_start = to_date(per["start_date"]) if per.get("start_date") else None
                if period_start and period_start > period_end:
                    print(f"config/period.yaml: start_date ({period_start}) > end_date ({period_end})")
                    return 2
            elif per.get("period"):
                _, period_end = parse_period(per["period"])
            else:
                print("Хугацаа алга: config/period.yaml-д start_date, end_date бичих эсвэл --date өгнө үү")
                return 2
            dates = [period_end]
            print(f"Хугацаа (config/period.yaml): {period_start or '(frequency-ээр)'} … {period_end}")
        elif period_start is None:
            # --date нь period.yaml-ийн end_date-тэй ижил бол start_date-ийг нь ашиглана (хоёр аргаар
            # ажиллуулахад :p_period_start ижил байх ёстой)
            per = load_period()
            if per.get("end_date") and per.get("start_date") and dates == [to_date(per["end_date"])]:
                period_start = to_date(per["start_date"])
        if len(dates) > 1 and not args.force:
            # Огнооны хүрээ (backfill): үзүүлэлт бүрийг өөрийн давтамжийн огноонуудаар л ажиллуулна
            plan = {d: [i for i in runnable if is_due(i.frequency, d)] for d in dates}
            plan = {d: inds for d, inds in plan.items() if inds}
        else:
            plan = {d: list(runnable) for d in dates}
    if not plan or not any(plan.values()) and not skipped:
        ids = _selected_ids(cat, args) or []
        if ids and all(cat.indicators[i].mode == "manual" for i in ids if i in cat.indicators):
            print(f"Ажиллуулах үзүүлэлт алга: сонгосон {len(ids)} үзүүлэлт гарын (manual) — "
                  f"python ri.py manual template … эсвэл тодорхойлолтод SQL бичнэ.")
            return 0
        print("Ажиллуулах үзүүлэлт алга.")
        return 0

    ctx = RunContext(cfg, mode="DRY_RUN" if args.dry_run else "RUN", save_csv=args.save_csv,
                     force=args.force, workers=args.workers or cfg.default_workers,
                     period_start=period_start, period_starts=period_starts, cat=cat)
    if cfg.env == "prod" and args.save_csv:
        print("prod орчинд --save-csv хэрэглэхгүй")
        return 2
    _setup_logging(ctx.run_id)
    with connect(cfg, cfg.result_connection) as conn:
        store.ensure_base(cfg, conn, log=logging.getLogger("ri").info)
    results = run_plan(ctx, plan, skipped)
    return 1 if has_problems(results, ctx) else 0


def cmd_verify(args) -> int:
    from .verify import verify_plan
    cfg, cat = _env(args.env)
    runnable, skipped = _select(cat, cfg, args)
    for ind, code, why in skipped:
        if code in ("INVALID_METADATA", "DEPENDENCY_CYCLE", "DEPENDENCY_MISSING"):
            print(f"  – {ind.indicator_id}: {code} {why[:150]}")
    period_starts = {parse_period(x)[1]: parse_period(x)[0] for x in args.period or []}
    dates = _dates(args)
    period_start = None
    if not dates:
        per = load_period()
        if not per.get("end_date"):
            print("Хугацаа алга: -p 2026-Q3, --date эсвэл config/period.yaml")
            return 2
        dates = [to_date(per["end_date"])]
        period_start = to_date(per["start_date"]) if per.get("start_date") else None
    ctx = RunContext(cfg, mode="VERIFY", cat=cat, period_start=period_start, period_starts=period_starts)
    orgmap.use(cfg)
    print(f"VERIFY env={cfg.env}: {len(runnable)} үзүүлэлт × {len(dates)} өдөр — source дээр дахин тооцоолж "
          f"{cfg.result_db}.{store.RESULT_TABLE}-тэй тулгана (бичихгүй)")
    return verify_plan(ctx, {d: list(runnable) for d in dates})


def cmd_auto(args) -> int:
    from .auto import build_plan, print_plan
    cfg, cat = _env(args.env)
    if not (args.indicator or args.activity or args.all or args.paths):
        args.all = True
    runnable, skipped = _select(cat, cfg, args)
    as_of = parse_date(args.as_of) if args.as_of else dt.date.today()
    since = parse_date(args.since) if args.since else as_of - dt.timedelta(days=366)
    ctx = RunContext(cfg, mode="RUN", force=True, workers=args.workers or cfg.default_workers, cat=cat)
    plan, items = build_plan(ctx, runnable, since, as_of)
    print_plan(items, since, as_of)
    if args.plan or not plan:
        return 0
    _setup_logging(ctx.run_id)
    results = run_plan(ctx, plan, [])
    return 1 if has_problems(results) else 0


def cmd_retry(args) -> int:
    cfg, cat = _env(args.env)
    with connect(cfg, cfg.result_connection) as conn:
        pairs = store.failed_from_run(cfg, conn, args.run_id)
    if not pairs:
        print(f"{args.run_id}: дахин ажиллуулах зүйл алга.")
        return 0
    # Эхний run-д ашигласан :p_period_start-ийг audit-аас аваад яг ижил хугацаагаар давтана
    groups: dict[tuple, list] = {}
    for iid, d, p_start in pairs:
        if iid in cat.indicators:
            key = (to_date(d), to_date(p_start) if p_start else None)
            groups.setdefault(key, []).append(cat.indicators[iid])
    _setup_logging()
    results = []
    for (d, p_start), inds in sorted(groups.items(), key=lambda kv: kv[0][0]):
        # Тооцооллын эхлэл үзүүлэлтийн period-оос дахин тодорхойлогдоно; report бол audit-ийн эхлэл
        ctx = RunContext(cfg, mode="RETRY", force=True, workers=args.workers or cfg.default_workers,
                         period_starts={d: p_start} if p_start else {}, cat=cat)
        results += run_plan(ctx, {d: inds}, [])
    return 1 if has_problems(results) else 0


def _resolve_ids(cat, args) -> list[str]:
    ids = _selected_ids(cat, args)
    for a in args.activity or []:
        ids += [x.indicator_id for x in cat.by_branch(a)]
    if getattr(args, "all", False):
        ids += list(cat.indicators)
    return sorted(set(ids))


def cmd_clean(args) -> int:
    cfg, cat = _env(args.env)
    if not cfg.allow_clean:
        print(f"{cfg.env} орчинд clean хориотой (config/{cfg.env}.yaml: allow_clean: false)")
        return 2
    ids = _resolve_ids(cat, args)
    acts = sorted({cat.resolve_activity(a).branch_id for a in args.activity or []}
                  | ({a.branch_id for a in cat.activities.values()} if args.all else set()) - {""})
    if not ids and not acts:
        print("--indicator, --activity эсвэл --all өгнө үү")
        return 2
    dates = _dates(args)
    d_from, d_to = (dates[0], dates[-1]) if dates else (None, None)
    with connect(cfg, cfg.result_connection) as conn:
        if not conn.table_exists(cfg.result_db, store.RESULT_TABLE):
            print(f"{cfg.result_db}.{store.RESULT_TABLE} алга — устгах зүйлгүй.")
            return 0
        counts, where, params = store.count_results(cfg, conn, ids, acts, d_from, d_to)
        for d, row_type, cnt in counts:
            print(f"  {cfg.result_db}.{store.RESULT_TABLE}  {to_date(d)}  {row_type:<9} {cnt} мөр")
        if args.audit:
            print(f"  + {cfg.result_db}.{store.AUDIT_TABLE}-ийн холбогдох бүртгэл")
        if not counts and not args.audit:
            print("Устгах зүйл олдсонгүй.")
            return 0
        if not args.yes and input("Устгах уу? (y/N): ").strip().lower() != "y":
            print("Цуцаллаа.")
            return 0
        if counts:
            store.delete_results(cfg, conn, where, params)
        aud = store.delete_audit(cfg, conn, ids, d_from, d_to) if args.audit and ids else 0
    print(f"Дууслаа: {sum(int(c) for *_, c in counts)} мөр устгав" + (f", {aud} audit" if args.audit else ""))
    return 0


def _print_table(cols, rows, limit, w=16):
    print("  ".join(f"{c[:w]:<{w}}" for c in cols))
    for r in rows[:limit]:
        cells = []
        for v in r:
            if isinstance(v, float):
                v = f"{v:.4g}"
            cells.append(f"{('' if v is None else str(v))[:w]:<{w}}")
        print("  ".join(cells))


def cmd_show(args) -> int:
    cfg, cat = _env(args.env)
    d = parse_date(args.date)
    with connect(cfg, cfg.result_connection) as conn:
        if not conn.table_exists(cfg.result_db, store.RESULT_TABLE):
            print(f"{cfg.result_db}.{store.RESULT_TABLE} хүснэгт хараахан үүсээгүй (init-db / run хийгээгүй).")
            return 0
        if args.activity:
            act = cat.resolve_activity(args.activity)
            cols, rows = store.read_activity(cfg, conn, act.branch_id, d)
            title = f"BRANCHID {act.branch_id} ({act.activity_id}) {act.name_mn}"
        elif args.indicator:
            iid = args.indicator.upper()
            if iid not in cat.indicators:
                print(f"Үзүүлэлт олдсонгүй: {iid}")
                return 2
            cols, rows = store.read_rows(cfg, conn, iid, d, args.level)
            title = f"{iid} {cat.indicators[iid].name_mn}"
        else:
            print("--indicator эсвэл --activity өгнө үү")
            return 2
    if not rows:
        print("Тухайн огноонд мөр алга.")
        return 0
    print(f"{cfg.result_db}.{store.RESULT_TABLE}  {title}  report_date={d}\n")
    hide = {"run_id", "sql_version"}
    idx = [i for i, c in enumerate(cols) if c.lower() not in hide]
    _print_table([cols[i] for i in idx], [[r[i] for i in idx] for r in rows], args.limit)
    print(f"\n{len(rows)} мөр (харуулсан: {min(len(rows), args.limit)})")
    return 0


def cmd_new_activity(args) -> int:
    folder = scaffold.new_activity(args.number, args.slug, args.name_mn, args.name_en,
                                   args.owner, args.reviewer, args.connection, args.frequency)
    print(f"Үүсгэлээ: {folder}")
    return 0


def cmd_new(args) -> int:
    for path in scaffold.new_indicator(args.activity, args.name_mn, args.name_en, args.connection,
                                       args.frequency, args.complexity, args.count, args.number):
        print(f"Үүсгэлээ: {path.parent.name}/{path.name}")
    return 0


def cmd_manual(args) -> int:
    if args.action == "template":
        cat = load_catalog()
        d = parse_date(args.date) if args.date else to_date(load_period()["end_date"])
        path = manual.write_template(cat, args.activity, d)
        print(f"Үүсгэлээ: {path}\nVALUE / VALUE_TEXT / SCORE / COMMENT баганыг бөглөөд:\n"
              f"  python ri.py manual load {path} --env <env>")
        return 0
    if not args.file or not args.env:
        print("manual load <файл> --env <env>")
        return 2
    cfg, cat = _env(args.env)
    return manual.load(cfg, cat, Path(args.file), parse_date(args.date) if args.date else None, args.dry_run)


def cmd_aggregate(args) -> int:
    """Үйл ажиллагааны нийт оноог ri_result-ийн одоогийн мөрүүдээс дахин тооцох."""
    cfg, cat = _env(args.env)
    acts = [cat.resolve_activity(a).activity_id for a in args.activity or []] or sorted(
        a.activity_id for a in cat.activities.values() if a.branch_id and not a.example)
    d = parse_date(args.date) if args.date else to_date(load_period()["end_date"])
    import uuid
    res = refresh_activities(cfg, cat, acts, d, str(uuid.uuid4()))
    print_activity_scores(res)
    return 0


def cmd_duplicates(args) -> int:
    """Нийтлэг тодорхойлолт (давхардлыг нэгтгэсэн) + нэгтгэгдээгүй ижил нэр (байх ёсгүй)."""
    from .dedup import norm_key
    cat = load_catalog()
    users: dict[str, list] = {}
    for i in cat.indicators.values():
        if i.calc or i.def_id:
            users.setdefault(i.calc or i.def_id, []).append(i)
    print(f"Нийтлэг тодорхойлолт (activities/_shared): {len(cat.calcs)} — "
          f"{sum(len(v) for v in users.values())} үзүүлэлт")
    for cid, calc in sorted(cat.calcs.items(), key=lambda kv: (-len(users.get(kv[0], [])), kv[0])):
        mode = "SQL" if calc.mode == "sql" else "гарын"
        print(f"  {cid} [{mode:<5} {calc.status:<11}] {len(users.get(cid, [])):>3} үйл ажиллагаа  {calc.name_mn[:60]}")
    by_name: dict[str, list] = {}
    for i in cat.indicators.values():
        if not (i.calc or i.def_id):
            by_name.setdefault(norm_key(i.name_mn), []).append(i)
    dup = {k: v for k, v in by_name.items() if len(v) > 1}
    if dup:
        print(f"\nНийтлэг тодорхойлолтгүй ижил нэр ({len(dup)}) — python ri.py import master.xlsx --update:")
        for _, inds in sorted(dup.items(), key=lambda kv: -len(kv[1]))[: args.limit]:
            print(f"  {len(inds):>3}× {inds[0].name_mn[:60]}: " + ", ".join(i.indicator_id for i in inds[:8]))
    else:
        print("\nНийтлэг тодорхойлолтгүй ижил нэр алга. Төстэй нэр, «гэр бүл»: python ri.py dedup master.xlsx")
    return 0


def cmd_dedup(args) -> int:
    """master-ийн давхардлыг хэрхэн шийдсэн: output/dedup_report.html (+ import_report.csv)."""
    from . import dedup
    from .config import OUTPUT_DIR
    from .importer import read_master
    rows, errors = read_master(Path(args.file), args.sheet)
    defs = dedup.decide(rows)
    cat = load_catalog()
    common = [d for d in defs if d.is_common]
    print(f"{len(rows)} мөр → {len(defs)} тодорхойлолт: нийтлэг {len(common)} ({sum(len(d.rows) for d in common)} мөр), "
          f"ганц {len(defs) - len(common)}; гэр бүл {len(dedup.families(defs))}, төстэй нэр {len(dedup.near_duplicates(defs))}")
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "dedup_report.html"
    path.write_text(dedup.report_html(rows, defs, cat), encoding="utf-8")
    print(f"Тайлан: {path}")
    if args.open:
        import webbrowser
        webbrowser.open(path.resolve().as_uri())
    return 1 if errors else 0


def cmd_report(args) -> int:
    from . import report
    cfg, cat = _env(args.env)
    d = parse_date(args.date) if args.date else to_date(load_period()["end_date"])
    keys = args.activity or [a.branch_id for a in cat.activities.values() if a.branch_id and not a.example]
    for key in keys:
        path = report.build(cfg, cat, key, d)
        print(f"Үүсгэлээ: {path}")
        if args.open:
            import webbrowser
            webbrowser.open(path.resolve().as_uri())
    return 0


def cmd_progress(args) -> int:
    cat = load_catalog()
    last = None
    if args.env:
        cfg = EnvConfig(args.env)
        with connect(cfg, cfg.result_connection) as conn:
            last = store.latest_status(cfg, conn)
    progress.report(cat, last)
    return 0


def cmd_test(args) -> int:
    """check → dry-run → test_dates run → show: нэг үзүүлэлтийг (SH_NNN бол бүх үйл ажиллагааг) бүтэн тестлэнэ."""
    iid = args.indicator.upper()
    cat = load_catalog()
    ind = cat.indicators.get(iid) or cat.calcs.get(iid)
    if ind is None:
        print(f"Үзүүлэлт олдсонгүй: {iid}")
        return 2
    ids = [iid]
    if ind.is_calc:                               # нийтлэг тодорхойлолт → түүнийг ашигладаг бүх үзүүлэлт
        ids = sorted(i.indicator_id for i in cat.indicators.values() if (i.calc or i.def_id) == iid)
        if not ids or ind.mode == "manual":
            print(f"{iid}: гарын (manual) эсвэл ашигладаг үзүүлэлт алга — тестлэх SQL байхгүй")
            return 2
    status_id = ind.def_id or iid                 # activity.yaml-ийн мөрийн төлөв нь тодорхойлолтод
    dates = list(ind.test_dates)
    if not dates:
        per = load_period()
        if per.get("end_date") or per.get("period"):
            dates = [to_date(per["end_date"]) if per.get("end_date") else parse_period(per["period"])[1]]
    if not dates:
        print(f"{iid}: test_dates хоосон, config/period.yaml ч алга — тохиргоонд test_dates бичнэ үү")
        return 2

    def run_args(**kw):
        base = dict(env=args.env, indicator=list(ids), activity=None, all=False, date=None, date_from=None,
                    date_to=None, test_dates=False, frequency=None, with_deps=False, dry_run=False,
                    save_csv=False, force=False, workers=None, paths=[], period=None)
        base.update(kw)
        return argparse.Namespace(**base)

    print(f"═══ 1/4 check ═══")
    if cmd_check(argparse.Namespace(indicator=list(ids), activity=None, paths=[], env=args.env)) != 0:
        print("\n✘ check алдаатай — засаад дахин ажиллуулна уу")
        return 1
    print(f"\n═══ 2/4 dry-run ({dates[0]}) ═══")
    if cmd_run(run_args(date=dates[0].isoformat(), dry_run=True)) != 0:
        print("\n✘ SQL ажиллахгүй байна — дээрх алдааг засна уу")
        return 1
    print(f"\n═══ 3/4 run ({', '.join(d.isoformat() for d in dates)}) ═══")
    if ind.test_dates:
        rc = cmd_run(run_args(test_dates=True, save_csv=args.env != "prod"))
    else:
        rc = cmd_run(run_args(date=dates[0].isoformat(), save_csv=args.env != "prod"))
    print(f"\n═══ 4/4 үр дүн ({dates[-1]}) ═══")
    if len(ids) > 1:
        print(f"{len(ids)} үйл ажиллагаанаас эхнийх нь; бусад: python ri.py show --env {args.env} -i <RI_…> -d {dates[-1]}")
    cmd_show(argparse.Namespace(env=args.env, indicator=ids[0], activity=None, level=None,
                                date=dates[-1].isoformat(), limit=args.limit))
    print("\n" + ("✔ Тест амжилттай. Тоог хуучин тайлантай тулгаад: "
                   f"python ri.py status {status_id} REVIEW --env {args.env}" if rc == 0
                   else "✘ Run-д алдаа/анхааруулга байна — дээрх хураангуйг харна уу"))
    return rc


def cmd_doctor(args) -> int:
    return tools.doctor(args.env)


def cmd_status(args) -> int:
    if not args.status:                                  # төлөвгүй бол: хаана байгааг харуулна
        return tools.describe(args.indicator)
    return tools.change_status(args.indicator, args.status, args.env, args.force)


def cmd_import(args) -> int:
    from .importer import import_master
    return import_master(args.file, args.sheet, args.owner, args.reviewer, args.connection,
                         args.frequency, args.shared_min, args.dry_run, args.group, update=args.update)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python ri.py", description="Risk indicator runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", help="Static шалгалт (DB шаардлагагүй)")
    s.add_argument("paths", nargs="*", help="Файл эсвэл folder (өгөхгүй бол бүгд)")
    s.add_argument("--indicator", "-i", action="append")
    s.add_argument("--activity", "-a", action="append")
    s.add_argument("--env", choices=ENVIRONMENTS, help="Тухайн орчны BRANCHID mapping, params-аар шалгах")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("init-db", help="ClickHouse-д riskassessment database, audit хүснэгт үүсгэх (байхгүй бол)")
    s.add_argument("--env", required=True, choices=ENVIRONMENTS)
    s.set_defaults(func=cmd_init_db)

    s = sub.add_parser("run", help="Үзүүлэлт ажиллуулах")
    _add_selection(s)
    s.add_argument("--test-dates", action="store_true", help="YAML-ийн test_dates огноонуудаар")
    s.add_argument("--frequency", choices=FREQUENCIES)
    s.add_argument("--with-deps", action="store_true", help="Хамаарах үзүүлэлтүүдийг хамт ажиллуулах")
    s.add_argument("--dry-run", action="store_true", help="SQL parse + багана шалгах, өгөгдөл бичихгүй")
    s.add_argument("--save-csv", action="store_true", help="Үр дүнг output/<env>/-д CSV болгох")
    s.add_argument("--force", action="store_true", help="Frequency-ийн due шалгалтыг алгасах")
    s.add_argument("--workers", type=int, help="Зэрэг ажиллах тоо")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("verify", help="Source дээр дахин тооцоолж ClickHouse-ийн үр дүнтэй тулгах (бичихгүй)")
    _add_selection(s)
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("auto", help="Дутуу / хуучирсан (үзүүлэлт × өдөр)-ийг л ажиллуулах (prod DAG)")
    _add_selection(s, required_date=False)
    s.add_argument("--plan", action="store_true", help="Юу, яагаад ажиллахыг харуулах (ажиллуулахгүй)")
    s.add_argument("--as-of", help="Өнөөдөр (default: өнөөдөр)")
    s.add_argument("--since", help="Хамгийн эртний тайлант өдөр (default: as-of − 1 жил)")
    s.add_argument("--workers", type=int)
    s.set_defaults(func=cmd_auto)

    s = sub.add_parser("retry", help="Тухайн run-ий амжилтгүйг дахин ажиллуулах")
    s.add_argument("--env", required=True, choices=ENVIRONMENTS)
    s.add_argument("--run-id", required=True)
    s.add_argument("--workers", type=int)
    s.set_defaults(func=cmd_retry)

    s = sub.add_parser("clean", help="Test-ийн үр дүнг устгах")
    _add_selection(s)
    s.add_argument("--audit", action="store_true", help="Audit бүртгэлийг ч устгах")
    s.add_argument("--yes", "-y", action="store_true", help="Баталгаажуулалт асуухгүй")
    s.set_defaults(func=cmd_clean)

    s = sub.add_parser("show", help="ri_result-ийн үр дүнг харах (үзүүлэлт эсвэл үйл ажиллагаа)")
    s.add_argument("--env", required=True, choices=ENVIRONMENTS)
    s.add_argument("--indicator", "-i")
    s.add_argument("--activity", "-a", help="Үйл ажиллагааны нийт оноо + үзүүлэлт бүрийн оноо")
    s.add_argument("--level", help="ACTIVITY / SOL (зөвхөн тэр түвшин)")
    s.add_argument("--date", "-d", required=True)
    s.add_argument("--limit", type=int, default=30)
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("new-activity", help="Шинэ activity folder үүсгэх")
    s.add_argument("--number", type=int, required=True, help="1–40")
    s.add_argument("--slug", required=True, help="англи snake_case: credit_risk")
    s.add_argument("--name-mn", required=True)
    s.add_argument("--name-en", required=True)
    s.add_argument("--owner", required=True)
    s.add_argument("--reviewer", required=True)
    s.add_argument("--connection", default="oracle_ra")
    s.add_argument("--frequency", default="monthly", choices=FREQUENCIES)
    s.set_defaults(func=cmd_new_activity)

    s = sub.add_parser("new", help="Activity-д шинэ үзүүлэлт (нэг .sql файл) үүсгэх")
    s.add_argument("--activity", "-a", required=True)
    s.add_argument("--name-mn", required=True)
    s.add_argument("--name-en", required=True)
    s.add_argument("--connection")
    s.add_argument("--frequency", choices=FREQUENCIES)
    s.add_argument("--complexity", default="simple", choices=["simple", "medium", "complex"])
    s.add_argument("--number", "-n", type=int, help="Master жагсаалтын № (өгөхгүй бол master-д байхгүй нэмэлт: 9001+)")
    s.add_argument("--count", type=int, default=1, help="Олныг нэг дор үүсгэх (нэрийг дараа засна)")
    s.set_defaults(func=cmd_new)

    envs = ENVIRONMENTS
    s = sub.add_parser("test", help="Нэг үзүүлэлтийг бүтэн тестлэх: check → dry-run → run → show")
    s.add_argument("indicator", help="RI_01_0002")
    s.add_argument("--env", default="dev", choices=envs)
    s.add_argument("--limit", type=int, default=15)
    s.set_defaults(func=cmd_test)

    s = sub.add_parser("doctor", help="Орчин шалгах: сангууд, .env, холболт, ClickHouse эрх")
    s.add_argument("--env", default="dev", choices=envs)
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("status", help="Хаана байгаа (RI_40_1545) / төлөв солих (тестийн үр дүнг шалгаад): SH_029 REVIEW")
    s.add_argument("indicator")
    s.add_argument("status", nargs="?", help="TODO / IN_PROGRESS / REVIEW / TESTED / DONE (өгөхгүй бол хаана байгааг)")
    s.add_argument("--env", choices=envs, help="Шалгах орчин (REVIEW→dev, TESTED→test, DONE→prod)")
    s.add_argument("--force", action="store_true", help="Шалгалтыг алгасах")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("import", help="Master жагсаалтаас (15 багана, xlsx/tsv/csv) үйл ажиллагаа, үзүүлэлт үүсгэх")
    s.add_argument("file", help="master.xlsx (Бүлэг | № | Үйл ажиллагаа | ... | Score | Scale | Автоматжуулах ...)")
    s.add_argument("--shared-min", type=int, default=2,
                   help="Хэдэн үйл ажиллагаанд давтагдвал нийтлэг тодорхойлолт (activities/_shared) болгох")
    s.add_argument("--group", "-g", type=int, action="append", help="Зөвхөн энэ бүлэг (олон удаа өгч болно)")
    s.add_argument("--sheet")
    s.add_argument("--owner", default="unassigned_owner")
    s.add_argument("--reviewer", default="unassigned_reviewer")
    s.add_argument("--connection", default="oracle_whouse")
    s.add_argument("--frequency", default="quarterly", choices=FREQUENCIES)
    s.add_argument("--dry-run", action="store_true", help="Юу үүсэхийг харуулах, файл бичихгүй")
    s.add_argument("--update", action="store_true",
                   help="Байгаа файлын master хэсгийг (нэр, жин, шатлал, хугацаа …) шинэчлэх — SQL-д хүрэхгүй")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("dedup", help="Master-ийн давхардлыг хэрхэн шийдсэн (HTML тайлан)")
    s.add_argument("file", help="master.xlsx")
    s.add_argument("--sheet")
    s.add_argument("--open", action="store_true")
    s.set_defaults(func=cmd_dedup)

    s = sub.add_parser("manual", help="Гараар оруулах үзүүлэлт: template (Excel) / load")
    s.add_argument("action", choices=["template", "load"])
    s.add_argument("file", nargs="?", help="load: бөглөсөн xlsx/csv")
    s.add_argument("--env", choices=envs)
    s.add_argument("--activity", "-a", action="append")
    s.add_argument("--date", "-d", help="Тайлант огноо (өгөхгүй бол period.yaml end_date)")
    s.add_argument("--dry-run", action="store_true", help="load: оноог харуулах, бичихгүй")
    s.set_defaults(func=cmd_manual)

    s = sub.add_parser("aggregate", help="Үйл ажиллагааны нийт оноог дахин тооцох")
    s.add_argument("--env", required=True, choices=envs)
    s.add_argument("--activity", "-a", action="append")
    s.add_argument("--date", "-d")
    s.set_defaults(func=cmd_aggregate)

    s = sub.add_parser("duplicates", help="Давхардсан / нийтлэг тооцоолол хуваалцсан үзүүлэлтүүд")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_duplicates)

    s = sub.add_parser("report", help="Үйл ажиллагааны тайлан (HTML): нийт оноо → бүлэг → үзүүлэлт → SOL")
    s.add_argument("--env", required=True, choices=envs)
    s.add_argument("--activity", "-a", action="append", help="BRANCHID (998) эсвэл ACT_01; өгөхгүй бол бүгд")
    s.add_argument("--date", "-d")
    s.add_argument("--open", action="store_true", help="Browser-т нээх")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("progress", help="Ахицын тайлан (+ --env өгвөл сүүлийн run-ийн төлөв)")
    s.add_argument("--env", choices=ENVIRONMENTS)
    s.set_defaults(func=cmd_progress)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, ValueError) as exc:
        print(f"Алдаа: {exc}")
        return 2
