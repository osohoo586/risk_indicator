"""Туслах командууд: doctor (орчин шалгах), import (master жагсаалт), status (төлөв солих)."""
import importlib
import os
import re
import sys
import time
from pathlib import Path

from . import orgmap, scaffold, store
from .checks import run_checks
from .config import (LOCAL_ENVIRONMENTS, PROJECT_ROOT, ConfigError, EnvConfig, load_dotenv, load_period,
                     vars_in)
from .db import connect
from .metadata import FREQUENCIES, STATUSES, apply_env_params, load_catalog, split_front_matter

OK, BAD, SKIP = "✔", "✘", "–"


# ── doctor ────────────────────────────────────────────────────────────────────
def doctor(env: str) -> int:
    """Орчныг нэг дор шалгаж тайлан гаргана. Алдаатай бол 1 буцаана."""
    problems = 0

    def line(mark, what, detail=""):
        nonlocal problems
        problems += mark == BAD
        print(f"  {mark} {what:<38} {detail}")

    print(f"\n[1] Python, сангууд")
    v = sys.version_info
    line(OK if v >= (3, 10) else BAD, f"Python {v.major}.{v.minor}", "" if v >= (3, 10) else "3.10+ хэрэгтэй")
    for mod, need in (("yaml", True), ("oracledb", True), ("clickhouse_connect", True), ("openpyxl", False)):
        try:
            m = importlib.import_module(mod)
            line(OK, mod, getattr(m, "__version__", ""))
        except ImportError:
            line(BAD if need else SKIP, mod, "pip install -r requirements.txt" if need else "зөвхөн import-д")

    print(f"\n[2] Тохиргоо")
    secrets = (PROJECT_ROOT / ".env").exists()
    load_dotenv()
    try:
        cfg = EnvConfig(env)
        line(OK, f"config/{env}.yaml", f"result → {cfg.result_connection}.{cfg.result_db}")
    except ConfigError as exc:
        line(BAD, f"config/{env}.yaml", str(exc))
        return 1
    cat = load_catalog()
    apply_env_params(cat, cfg)
    used = ({i.connection for i in cat.indicators.values()} | {cfg.result_connection}
            | {(cfg.raw.get(k) or {}).get("connection") for k in ("org", "audit")}) & set(cfg.connections)
    # Шинэ машин: аль ${VAR} дутууг холболтоор нь (ашиглагдах холболтынх л заавал)
    missing = {n: [v for v in vars_in(cfg.connections[n]) if not os.environ.get(v)] for n in cfg.connections}
    need = sorted({v for n in used for v in missing[n]})
    if env in LOCAL_ENVIRONMENTS:            # local: docker-ийн default нууц үг (config/local.yaml)
        line(OK if secrets else SKIP, ".env", "" if secrets else f"{env}-д заавал биш (docker default)")
    elif secrets or not need:                # файл эсвэл серверийн env хувьсагч (Airflow, CI) — аль нь ч болно
        line(OK, ".env" if secrets else "env хувьсагч", "" if secrets else "файлгүй — орчны хувьсагчаас")
    else:
        line(BAD, ".env", "cp .env.example .env — дараа нь доорх хувьсагчдыг бөглөнө")
    if need:
        line(BAD, "Дутуу хувьсагч", ", ".join(need))
    other = sorted({v for n in set(cfg.connections) - used for v in missing[n]})
    if other:
        line(SKIP, "Ашиглагдаагүй холболтын хувьсагч", ", ".join(other) + " (заавал биш)")
    per = load_period()
    line(OK if per else SKIP, "config/period.yaml",
         f"{per.get('start_date', '')} … {per.get('end_date') or per.get('period', '')}" if per else "алга (--date ашиглана)")
    orgmap.use(cfg)
    line(OK, "BRANCHID → SOLID", orgmap.source())
    line(OK, "Аудитын огноо", orgmap.audit_source())
    errors, warnings = run_checks(cat)
    line(OK if not errors else BAD, f"Үзүүлэлтүүд ({len(cat.indicators)})",
         f"{len(errors)} алдаа, {len(warnings)} анхааруулга" + (" → python ri.py check" if errors else ""))

    print(f"\n[3] Холболтууд ({env})")
    for name in cfg.connections:
        users = sum(1 for i in cat.indicators.values() if i.connection == name)
        label = f"{name} ({cfg.connections[name].get('type')})"
        try:
            t0 = time.time()
            with connect(cfg, name) as conn:
                probe = "SELECT 1 FROM dual" if conn.type == "oracle" and cfg.connections[name]["type"] == "oracle" \
                    else "SELECT 1"
                conn.query(probe, {})
            line(OK, label, f"{(time.time() - t0) * 1000:.0f}ms, {users} үзүүлэлт")
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).splitlines()[0][:90]
            line(BAD if name in used else SKIP, label,
                 msg if name in used else f"ашиглагдаагүй ({msg[:50]})")

    print(f"\n[4] ClickHouse эрх ({cfg.result_db})")
    try:
        with connect(cfg, cfg.result_connection) as ch:
            _, rows = ch.query("SELECT count() FROM system.databases WHERE name = {d:String}", {"d": cfg.result_db})
            exists = bool(rows[0][0])
            line(OK if exists else SKIP, f"database {cfg.result_db}",
                 "байна" if exists else "алга → python ri.py init-db")
            for t in (store.AUDIT_TABLE, store.HISTORY_TABLE):
                line(OK if ch.table_exists(cfg.result_db, t) else SKIP, t,
                     "" if ch.table_exists(cfg.result_db, t) else "алга → python ri.py init-db")
            if exists:
                tmp = f"`{cfg.result_db}`.`__ri_doctor_{int(time.time())}`"
                for what, sql in (("CREATE TABLE", f"CREATE TABLE {tmp} (d Date, x Int64) ENGINE = MergeTree ORDER BY d"),
                                  ("INSERT", f"INSERT INTO {tmp} VALUES ('2026-01-01', 1)"),
                                  ("ALTER ADD COLUMN", f"ALTER TABLE {tmp} ADD COLUMN y Nullable(String)"),
                                  ("DELETE", f"DELETE FROM {tmp} WHERE x = 1"),
                                  ("DROP TABLE", f"DROP TABLE {tmp} SYNC")):
                    try:
                        ch.execute(sql)
                        line(OK, f"эрх: {what}")
                    except Exception as exc:  # noqa: BLE001
                        line(BAD, f"эрх: {what}", str(exc).splitlines()[0][:80])
                try:
                    ch.execute(f"DROP TABLE IF EXISTS {tmp} SYNC")
                except Exception:
                    pass
    except Exception as exc:  # noqa: BLE001
        line(BAD, f"{cfg.result_connection}", str(exc).splitlines()[0][:90])

    print(f"\n{'Бүгд хэвийн.' if not problems else f'{problems} асуудал олдлоо (✘).'}")
    return 1 if problems else 0


# ── status ────────────────────────────────────────────────────────────────────
DEFAULT_STATUS_ENV = {"REVIEW": "dev", "TESTED": "test", "DONE": "prod"}


def set_status_in_file(path: Path, new_status: str) -> str:
    """Файлын тохиргоон дахь status-ийг солино. Хуучин төлөвийг буцаана."""
    text = path.read_text(encoding="utf-8")
    meta, body = split_front_matter(text)
    if meta is None:
        raise ValueError(f"{path}: тохиргоо (/*--- ---*/) алга")
    m = re.search(r"^status:[ \t]*([A-Z_]+)", meta, re.M)
    if not m:
        raise ValueError(f"{path}: тохиргоонд status мөр алга")
    new_meta = meta[:m.start(1)] + new_status + meta[m.end(1):]
    path.write_text(text.replace(meta, new_meta, 1), encoding="utf-8")
    return m.group(1)


def describe(indicator_id: str) -> int:
    """Үзүүлэлт / тодорхойлолт хаана байна: файл, activity.yaml-ийн мөр, нийтлэг тодорхойлолт, горим, төлөв."""
    cat = load_catalog()
    iid = indicator_id.upper()
    ind = cat.get(iid)
    if ind is None:
        print(f"Үзүүлэлт олдсонгүй: {iid}")
        return 2
    rel = lambda path: path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path  # noqa: E731
    print(f"{iid}  {ind.name_mn}")
    if ind.is_calc:
        users = sorted(i.indicator_id for i in cat.indicators.values() if (i.calc or i.def_id) == iid)
        acts = sorted({cat.indicators[u].activity_id for u in users})
        print(f"  Нийтлэг тодорхойлолт: {rel(ind.file_path)}")
        print(f"  Горим: {'гарын (manual)' if ind.mode == 'manual' else 'SQL'}   төлөв: {ind.status}   "
              f"хугацаа: {ind.period}")
        print(f"  {len(users)} үзүүлэлт, {len(acts)} үйл ажиллагаа: {', '.join(users[:10])}"
              + (" …" if len(users) > 10 else ""))
        if ind.sql_from:
            print(f"  SQL: {ind.sql_from}-ийнх (params: {ind.params})")
        return 0
    act = cat.activities[ind.activity_id]
    print(f"  Үйл ажиллагаа: {act.activity_id} {act.name_mn} (BRANCHID {act.branch_id or 'алга'})")
    if ind.manifest is not None:
        d = cat.calcs[ind.def_id]
        diff = sorted(set(ind.manifest) - {"id", "def", "weight"})
        print(f"  Мөр: {rel(Path(act.folder) / 'activity.yaml')}  shared: {{id: {iid}, def: {ind.def_id}, weight: {ind.manifest.get('weight')}}}")
        print(f"  Тодорхойлолт: {rel(d.file_path)} ({'гарын' if d.mode == 'manual' else 'SQL'}, төлөв {d.status})"
              + (f"; энэ үйл ажиллагаанд дарсан: {', '.join(diff)}" if diff else ""))
    else:
        print(f"  Файл: {rel(ind.file_path)}" + (f" (SQL нь {ind.sql_from}-ийнх)" if ind.sql_from else ""))
    print(f"  Горим: {ind.mode}   төлөв: {ind.status}   жин: {ind.weight}   хугацаа: {ind.period}"
          + ("   шатлал задарсангүй — master-ийг засна" if ind.scale_error else ""))
    return 0


def change_status(indicator_id: str, new_status: str, env: str | None, force: bool) -> int:
    new_status = new_status.upper()
    if new_status not in STATUSES:
        print(f"Төлөв буруу: {new_status}. Боломжит: {', '.join(STATUSES)}")
        return 2
    cat = load_catalog()
    iid = indicator_id.upper()
    ind = cat.get(iid)
    if ind is None:
        print(f"Үзүүлэлт олдсонгүй: {iid}")
        return 2
    if ind.manifest is not None:                # activity.yaml shared: — төлөв нь нийтлэг тодорхойлолтод
        n = sum(1 for i in cat.indicators.values() if (i.calc or i.def_id) == ind.def_id)
        print(f"{iid}-ийн төлөв нийтлэг тодорхойлолт {ind.def_id}-д ({n} үйл ажиллагаа): "
              f"python ri.py status {ind.def_id} {new_status}" + (f" --env {env}" if env else ""))
        return 2
    cur = ind.status
    problems = []
    order = STATUSES.index
    if new_status in DEFAULT_STATUS_ENV:
        if order(new_status) > order(cur) + 1:
            problems.append(f"{cur} → {new_status}: шат алгасаж болохгүй ({STATUSES[order(cur) + 1]} эхэлж)")
        users = [i.indicator_id for i in cat.indicators.values() if (i.calc or i.def_id) == iid] or [iid]
        errors, _ = run_checks(cat, [u for u in users if u in cat.indicators])
        if errors:
            problems.append(f"python ri.py check: {len(errors)} алдаа")
        env = env or DEFAULT_STATUS_ENV[new_status]
        try:
            cfg = EnvConfig(env)
            with connect(cfg, cfg.result_connection) as ch:
                latest = store.latest_status(cfg, ch)
            runs = [latest[u] for u in users if u in latest]
            bad = [u for u in users if u in latest and latest[u]["status"] not in ("SUCCESS", "WARNING")]
            if not runs:
                problems.append(f"{env} орчинд ажиллаж байгаагүй (python ri.py test {users[0]} --env {env})")
            elif bad:
                problems.append(f"{env} дээрх сүүлийн run амжилтгүй: {', '.join(bad[:5])}")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{env} орчны audit-ийг уншиж чадсангүй: {str(exc).splitlines()[0][:80]}")
    if problems and not force:
        print(f"{iid}: {cur} → {new_status} хийх боломжгүй:")
        for p in problems:
            print(f"  ✘ {p}")
        print("  (Шалгалтыг алгасах бол --force)")
        return 1
    old = set_status_in_file(ind.file_path, new_status)
    print(f"{iid}: {old} → {new_status}  ({ind.file_path.relative_to(PROJECT_ROOT)})"
          + ("  [--force]" if problems else ""))
    return 0
