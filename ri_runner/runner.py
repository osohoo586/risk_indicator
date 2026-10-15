"""Main runner.

Урсгал (тайлант огноо бүрт):
  1. Сонгосон үзүүлэлтүүдийг ТООЦООЛЛООР × хугацааны эхлэлээр бүлэглэнэ: өөрийн SQL (sql) эсвэл нийтлэг
     (_shared, calc). Хугацаа нь үзүүлэлтийн `period` (report / last_year / since_audit / latest) ба үйл
     ажиллагааны аудитын огнооноос. manual үзүүлэлт run-д орохгүй (ri.py manual).
  2. Тооцоолол бүрийг НЭГ удаа ажиллуулна (dependency дарааллаар, зэрэг). Source (Oracle / ClickHouse)-ийг
     ЗӨВХӨН уншина (db.connect(..., read_only=True)); бичих цорын ганц газар нь result ClickHouse.
  3. Үзүүлэлт бүрд: тооцооллын мөрүүдээс өөрийн үйл ажиллагааны утгыг гаргана
       SOL мөр      → үйл ажиллагааны BRANCHID-ийн SOL-уудаар нэгтгэнэ (Σnumerator / Σdenominator)
       ACTIVITY мөр → өөрийн BRANCHID-тай мөр;  BANK мөр → банк нийтийн утга
     → шатлалаар оноо (1–5) → ri_result-д НЭГ мөр (result_number = утга, result = оноо, solid = SOLID-ууд)
     → буцааж уншиж тулгана (зөрвөл устгаад FAILED). SOL задаргаа нь зөвхөн дотоод (verify, --save-csv).
  4. Хөндөгдсөн үйл ажиллагаа бүрийн нийт оноо → ri_result (risk_ind_id = TOTAL, result = түвшин).
"""
import csv
import datetime as dt
import getpass
import json
import logging
import os
import threading
import time
import uuid
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter

from . import orgmap, store
from .config import LOGS_DIR, OUTPUT_DIR, EnvConfig, load_scoring
from .dates import is_due, period_params, with_aliases
from .db import ConnectionPool, Connector, RunnerError, classify_error, connect, convert_value
from .metadata import STATUSES, Activity, Catalog, Indicator
from .scale import UNELEHGUI, compute_score, risk_level
from .sqltext import clean_trailing, expand_shared, is_plsql_block, render_schemas

OK_STATUSES = {"SUCCESS", "WARNING", "DRY_RUN_OK"}
PROBLEM_STATUSES = {"FAILED", "TIMEOUT", "VALIDATION_FAILED"}
log = logging.getLogger("ri")


CONFIG_SKIPS = {"INVALID_METADATA", "DEPENDENCY_MISSING", "DEPENDENCY_CYCLE"}   # тохиргооны алдаа: ажиллахгүй
_REPLACED_LOCK = threading.Lock()


def has_problems(results, ctx: "RunContext | None" = None) -> bool:
    """Exit code-д: алдаа, тохиргооны алдаа, source бэлэн биш эсвэл хуучин мөр устаагүй бол True."""
    return (any(r.status in PROBLEM_STATUSES or r.error_code in CONFIG_SKIPS | {"SOURCE_NOT_READY"} for r in results)
            or bool(ctx is not None and getattr(ctx, "replace_failed", False)))


def prep_sql(text: str, cfg: EnvConfig) -> str:
    """{{shared.x}}, {{schema.x}}-ийг задалсан, ажиллахад бэлэн SQL."""
    return clean_trailing(render_schemas(expand_shared(text), cfg.schemas))


@dataclass
class Outcome:
    indicator: Indicator
    report_date: dt.date
    status: str
    started_at: dt.datetime
    finished_at: dt.datetime
    error_code: str | None = None
    error_message: str | None = None
    source_row_count: int | None = None
    result_row_count: int | None = None
    affected_rows: int | None = None
    checks: list = field(default_factory=list)      # [(name, PASS/WARN/FAIL/INFO, message)]
    period_start: dt.date | None = None
    value: float | None = None
    score: float | None = None

    @property
    def duration(self) -> float:
        return round((self.finished_at - self.started_at).total_seconds(), 3)

    @property
    def check_text(self) -> str:
        return "; ".join(f"{s}:{n}:{m}" for n, s, m in self.checks if s != "PASS")

    @property
    def problem_text(self) -> str:
        return "; ".join(f"{s}:{n}:{m}" for n, s, m in self.checks if s in ("WARN", "FAIL"))


@dataclass
class RunContext:
    cfg: EnvConfig
    cat: Catalog | None = None
    mode: str = "RUN"                 # RUN / DRY_RUN / RETRY
    save_csv: bool = False
    force: bool = False
    workers: int = 1
    period_start: dt.date | None = None
    period_starts: dict = field(default_factory=dict)      # {тайлант өдөр: эхлэл} (-p 2026-Q3)
    replaced: list = field(default_factory=list)            # [(indicator_id, тайлант өдөр)] — run_date-ийн төгсгөлд
    replace_failed: bool = False
    pool: ConnectionPool | None = None                      # run-ий турш thread бүрт connection (run_plan нээж хаана)

    def conn(self, name: str, read_only: bool = False) -> Connector:
        return self.pool.get(name, read_only) if self.pool is not None else connect(self.cfg, name, read_only)
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    executed_by: str = field(default_factory=lambda: os.environ.get("RI_USER") or getpass.getuser())


# ── Сонголт ────────────────────────────────────────────────────────────────────
def select(cat: Catalog, cfg: EnvConfig, indicator_ids=None, activity_ids=None, all_=False,
           frequency=None, with_deps=False) -> tuple[list[Indicator], list[tuple[Indicator, str, str]]]:
    """(ажиллуулах үзүүлэлтүүд, [(үзүүлэлт, код, шалтгаан)] алгасах). manual үзүүлэлт орохгүй."""
    picked: dict[str, Indicator] = {}
    for iid in indicator_ids or []:
        iid = iid.upper()
        if iid not in cat.indicators:
            raise ValueError(f"Үзүүлэлт олдсонгүй: {iid}")
        picked[iid] = cat.indicators[iid]
    for key in activity_ids or []:
        for ind in cat.by_branch(key):                       # BRANCHID (998) эсвэл ACT_01
            picked[ind.indicator_id] = ind
    if all_:
        for ind in cat.indicators.values():
            if not ind.example:
                picked[ind.indicator_id] = ind
    if frequency:
        picked = {k: v for k, v in picked.items() if v.frequency == frequency}
    if with_deps:
        stack = list(picked)
        while stack:
            for dep in cat.indicators[stack.pop()].dependencies:
                if dep in cat.indicators and dep not in picked:
                    picked[dep] = cat.indicators[dep]
                    stack.append(dep)

    runnable, skipped = [], []
    min_idx = STATUSES.index(cfg.min_status)
    explicit = {i.upper() for i in indicator_ids or []}      # local/dev: -i-ээр нэрлэсэн бол status-аас үл хамаарна
    for ind in sorted(picked.values(), key=lambda i: i.indicator_id):
        if ind.mode == "manual":
            continue
        calc = cat.calcs.get(ind.calc) if ind.mode == "shared" else ind
        errs = list(ind.errors) + (list(calc.errors) if calc is not None and calc is not ind else [])
        if ind.mode == "shared" and calc is None:
            errs.append(f"calc {ind.calc} олдсонгүй (activities/_shared)")
        if errs:
            skipped.append((ind, "INVALID_METADATA", "; ".join(errs)))
        elif not ind.enabled:
            skipped.append((ind, "DISABLED", "enabled: false"))
        elif any(str(v).strip().upper() == "TODO" for v in effective_params(cat, ind).values()):
            todo = [k for k, v in effective_params(cat, ind).items() if str(v).strip().upper() == "TODO"]
            skipped.append((ind, "PARAMS_TODO", f"params бөглөөгүй: {', '.join(todo)}"))
        elif STATUSES.index(ind.status) < min_idx and not (
                ind.indicator_id in explicit and cfg.env in ("local", "dev")):
            skipped.append((ind, "STATUS_BELOW_MIN",
                            f"status={ind.status}, {cfg.env} орчинд min_status={cfg.min_status}"))
        elif calc is not ind and STATUSES.index(calc.status) < min_idx:
            skipped.append((ind, "STATUS_BELOW_MIN", f"{calc.indicator_id} (нийтлэг SQL) status={calc.status}"))
        else:
            runnable.append(ind)
    return _dependency_problems(cat, runnable, skipped)


def effective_params(cat: Catalog | None, ind: Indicator) -> dict:
    """Тодорхойлолтын (нийтлэг SQL) params + энэ үзүүлэлтийн (activity.yaml / файл) params."""
    calc = cat.calcs.get(ind.calc) if cat is not None and ind.mode == "shared" and ind.calc else None
    return {**(calc.params if calc is not None else {}), **ind.params}


def _dependency_problems(cat: Catalog, runnable: list[Indicator], skipped: list) -> tuple[list, list]:
    """Байхгүй dependency (DEPENDENCY_MISSING), тойрог A → B → A (DEPENDENCY_CYCLE), ажиллахгүй dependency-тэй
    (тохиргоо алдаатай, disabled — шилжилтээр) үзүүлэлтийг алгасна. Бусад нь ажилласаар (run унахгүй)."""
    blocked = {i.indicator_id: code for i, code, _ in skipped if code not in ("STATUS_BELOW_MIN", "PARAMS_TODO")}
    ok = list(runnable)
    while True:
        changed = False
        for ind in list(ok):
            missing = [x for x in ind.dependencies if cat.get(x) is None]
            dep = next((x for x in ind.dependencies if x in blocked
                        or (cat.get(x) is not None and (cat.get(x).errors or not cat.get(x).enabled))), None)
            if missing:
                code, why = "DEPENDENCY_MISSING", f"dependency олдсонгүй: {', '.join(missing)}"
            elif dep:
                code, why = "DEPENDENCY_FAILED", f"{dep} ажиллахгүй ({blocked.get(dep, 'тохиргоо алдаатай / disabled')})"
            else:
                continue
            skipped.append((ind, code, why))
            blocked[ind.indicator_id] = code
            ok.remove(ind)
            changed = True
        ids = {i.indicator_id for i in ok}
        try:
            TopologicalSorter({i.indicator_id: [x for x in i.dependencies if x in ids] for i in ok}).prepare()
        except CycleError as exc:
            cycle = exc.args[1]
            for ind in [i for i in ok if i.indicator_id in cycle]:
                skipped.append((ind, "DEPENDENCY_CYCLE", f"dependency тойрог: {' -> '.join(cycle)}"))
                blocked[ind.indicator_id] = "DEPENDENCY_CYCLE"
                ok.remove(ind)
            changed = True
        if not changed:
            return ok, skipped


def period_start_for(ctx: "RunContext", ind: Indicator, act: Activity | None, d: dt.date) -> tuple[dt.date, str]:
    """(хугацааны эхлэл, тайлбар) — үзүүлэлтийн period-оор (master-ийн "Хамрах хугацаа")."""
    if ind.period == "last_year":
        start = _year_back(d) + dt.timedelta(days=1)
        return start, "сүүлийн 1 жил"
    if ind.period == "since_audit":
        audit = orgmap.audit_date(act, d) if act is not None else None     # DB (GRC) эсвэл activity_map.csv
        if audit:
            return audit, f"аудитаас хойш ({audit})"
        return _year_back(d) + dt.timedelta(days=1), "аудитын огноо алга → сүүлийн 1 жил"
    start = ctx.period_starts.get(d) or ctx.period_start or period_params(ind.frequency, d)["p_period_start"]
    return start, "тайлант хугацаа"


def _year_back(d: dt.date) -> dt.date:
    try:
        return d.replace(year=d.year - 1)
    except ValueError:                       # 02-29
        return d.replace(year=d.year - 1, day=28)


def quarters_between(start: dt.date, d: dt.date) -> int:
    """[start, d] хугацаанд хамаарах улирлын тоо (≥ 1) — "улирлын дундаж"-ийн хуваарь."""
    q1, q2 = start.year * 4 + (start.month - 1) // 3, d.year * 4 + (d.month - 1) // 3
    return max(1, q2 - q1 + 1)


def group_by_calc(ctx: "RunContext", targets: list[Indicator], d: dt.date) -> dict[str, tuple]:
    """{"calc_id@эхлэл": (тооцоолол, хугацааны эхлэл, [үзүүлэлтүүд])} — нэг тооцоолол нэг хугацаанд НЭГ удаа."""
    cat = ctx.cat
    groups: dict[str, tuple] = {}
    for t in targets:
        calc = cat.calcs[t.calc] if t.mode == "shared" else t
        start, _ = period_start_for(ctx, t, cat.activities.get(t.activity_id), d)
        key = f"{calc.indicator_id}@{start}"
        if t.params and calc is not t:            # энэ үйл ажиллагааны өөр params → тусдаа ажиллуулна
            key += "@" + json.dumps(t.params, sort_keys=True, default=str)
        if calc is not t and _uses_activity_branch(calc):    # SQL нь :p_activity_branch_id → үйл ажиллагаа бүрт
            key += f"@{t.activity_id}"
        groups.setdefault(key, (calc, start, []))[2].append(t)
    return groups


def _uses_activity_branch(calc: Indicator) -> bool:
    try:
        sql = calc.read_sql()
    except OSError:
        return False
    return ":p_activity_branch_id" in sql or "{p_activity_branch_id" in sql


# ── Утга нэгтгэх, оноо ────────────────────────────────────────────────────────
def aggregate(rows: list[dict], rule_by_metric: dict | None = None) -> dict[str, dict]:
    """{metric: {numerator, denominator, value, source_row_count, data_status}}.

    NUMERATOR/DENOMINATOR байвал Σnumerator / Σdenominator (харьцааны ДУНДАЖ БИШ),
    DENOMINATOR байхгүй эсвэл rollup_metrics-д 'sum' гэвэл ΣVALUE (жнь тоо: гомдол, зөрчил).
    """
    rule_by_metric = rule_by_metric or {}
    by_metric = defaultdict(list)
    for r in rows:
        by_metric[r["metric"]].append(r)
    out = {}
    for m, rs in by_metric.items():
        nums = [r["numerator"] for r in rs if r["numerator"] is not None]
        dens = [r["denominator"] for r in rs if r["denominator"] is not None]
        num = sum(nums) if nums else None
        den = sum(dens) if dens else None
        status = "OK"
        if rule_by_metric.get(m) == "sum" or den is None:
            vals = [r["value"] for r in rs if r["value"] is not None]
            value = sum(vals) if vals else None
        else:
            value = (num / den) if (num is not None and den) else None
            if den == 0:
                status = "ZERO_DENOMINATOR"
        src = [r["source_row_count"] for r in rs if r.get("source_row_count") is not None]
        texts = sorted({str(r["value_text"]) for r in rs if r.get("value_text") not in (None, "")})
        if value is None and status == "OK" and not texts:      # зөвхөн VALUE_TEXT-тэй (ангилал) бол OK
            status = "NO_DATA"
        out[m] = {"numerator": num, "denominator": den, "value": value, "data_status": status,
                  "source_row_count": int(sum(src)) if src else None, "value_texts": texts}
    return out


def score_value(ind: Indicator, value, value_text=None):
    """(score float|None, label, status, сонгосон текст). None = үнэлэхгүй / шатлалгүй (жингээс хасагдана).

    value_text (жнь "ДАГ-т гомдол ирж, шалгагдсан.") нь ангиллын мөрөөр оноо авна. Тоон утга ба текстийн
    аль өндөр оноо нь (master: "3-аас дээш гомдол = 4, ДАГ-т ирсэн бол = 5").
    """
    if not ind.scale:
        return None, "Шатлал тодорхойлогдоогүй", "NO_SCALE", None
    texts = [value_text] if isinstance(value_text, str) else list(value_text or [])
    best = (None, None, None)
    for raw in ([value] if value is not None or not texts else []) + texts:
        s, label = compute_score(ind.scale, raw, value_unit=ind.value_unit)
        if s is not None and s != UNELEHGUI and (best[0] is None or float(s) > best[0]):
            best = (float(s), label, raw if isinstance(raw, str) else None)
    if best[0] is None:
        s, label = compute_score(ind.scale, value if value is not None else (texts[0] if texts else None),
                                 value_unit=ind.value_unit)
        return None, label or UNELEHGUI, "UNELEHGUI", None
    return best[0], best[1], "OK", best[2]


def activity_rows(ind: Indicator, act: Activity, calc_rows: list[dict], d: dt.date, rules: dict | None = None):
    """Тооцооллын мөрүүдээс энэ үйл ажиллагааных: ({metric: agg}, drill-down мөрүүд, шалгалтууд).

    rules: rollup_metrics (үзүүлэлтийнх, эс бөгөөс нийтлэг тооцооллынх)."""
    levels = {r["entity_level"] for r in calc_rows}
    rules = rules if rules is not None else ind.rollup_metrics
    checks = []
    if "SOL" in levels:
        if not act.branch_id:
            raise RunnerError("BRANCH_NOT_MAPPED",
                              f"{act.activity_id}-д BRANCHID тохируулаагүй (config/activity_map.csv)")
        sols = orgmap.sols_for(act.branch_id, d)
        if not sols:
            checks.append(("units", "WARN", f"BRANCHID {act.branch_id}-д {d}-нд SOL алга (activity_units)"))
        key = {_sol_key(k): k for k in sols}             # "0809" == "809"
        chosen = [dict(r, entity_name=r["entity_name"] or sols.get(key[_sol_key(r["entity_id"])]))
                  for r in calc_rows if r["entity_level"] == "SOL" and _sol_key(r["entity_id"]) in key]
        missing = sorted(set(key) - {_sol_key(r["entity_id"]) for r in chosen})
        sol_rows = [r for r in calc_rows if r["entity_level"] == "SOL"]
        if sols and sol_rows and not chosen:
            sample = ", ".join(sorted({r["entity_id"] for r in sol_rows})[:5])
            checks.append(("units_match", "WARN", f"SQL-ийн {len(sol_rows)} SOL мөрөөс BRANCHID {act.branch_id}-ийн "
                                                   f"SOL-тай нэг ч таарсангүй (SQL: {sample} …) — ENTITY_ID-г шалга"))
        elif sols and missing:
            checks.append(("units_no_data", "INFO", f"{len(missing)} SOL-д мөр алга: {', '.join(missing[:10])}"))
        return aggregate(chosen, rules), chosen, checks
    if "ACTIVITY" in levels:
        act_rows = [r for r in calc_rows if r["entity_level"] == "ACTIVITY"]
        mine = [r for r in act_rows if r["entity_id"] == str(act.branch_id)]
        if not mine and ind.mode == "sql" and len({r["entity_id"] for r in act_rows}) == 1:
            mine = act_rows                  # өөрийн SQL нэг л ACTIVITY мөр буцаасан (ENTITY_ID нь өөр нэршилтэй)
        if not mine:                         # нийтлэг тодорхойлолтод энэ BRANCHID-ийн мөр алга → өгөгдөл алга
            checks.append(("activity_row", "INFO", f"ACTIVITY мөрүүдээс BRANCHID {act.branch_id} олдсонгүй"))
        return aggregate(mine, rules), [], checks
    if "BANK" in levels:
        return aggregate([r for r in calc_rows if r["entity_level"] == "BANK"], rules), [], checks
    return aggregate(calc_rows, rules), calc_rows, checks


def activity_sol_ids(act: Activity, d: dt.date) -> str:
    """Үйл ажиллагааны (BRANCHID) тайлант өдрийн SOLID-ууд: "808,810,811" — ri_result.solid metadata."""
    if not act.branch_id:
        return ""
    try:
        sols = orgmap.sols_for(act.branch_id, d)
    except Exception:  # noqa: BLE001 — metadata; тооцоолол өөрөө алдааг мэдэгдэнэ
        return ""
    return ",".join(sorted(sols, key=lambda x: (len(x), x)))


def version_of(cat: Catalog, ind: Indicator) -> str:
    """audit/ri_result-ийн sql_version: үзүүлэлтийн файл (+ shared горимд нийтлэг тооцооллын файл)
    + орчны params (config-оор дарсан бол) — өөрчлөгдвөл auto дахин ажиллуулна."""
    v = ind.sql_version
    if ind.mode == "shared" and ind.calc in cat.calcs:
        v = f"{v}|{cat.calcs[ind.calc].sql_version}"
    params = effective_params(cat, ind)
    if params:
        import hashlib
        v += "|p" + hashlib.sha1(json.dumps(params, sort_keys=True, default=str).encode()).hexdigest()[:6]
    return v


def _sol_key(v: str) -> str:
    s = str(v).strip()
    return (s.lstrip("0") or "0") if s.isdigit() else s


def validate_calc(calc: Indicator, rows: list[dict]) -> list:
    """Бичихээс өмнөх шалгалт (тооцооллын мөрүүд дээр)."""
    if not rows:
        st = "FAIL" if calc.empty_source == "fail" or calc.min_rows else "WARN"
        return [("no_source_data", st, "SQL 0 мөр буцаалаа")]
    checks = []
    if calc.min_rows and len(rows) < calc.min_rows:
        checks.append(("min_rows", "FAIL", f"{len(rows)} мөр гарсан, хамгийн багадаа {calc.min_rows} (source дутуу?)"))
    keys = [(r["entity_level"], r["entity_id"], r["metric"]) for r in rows]
    dup = len(keys) - len(set(keys))
    checks.append(("duplicate", "FAIL" if dup else "PASS",
                   f"{dup} мөр давхардсан (ENTITY_LEVEL, ENTITY_ID, METRIC)" if dup else ""))
    bad_level = sorted({r["entity_level"] for r in rows if not r["entity_level"]})
    empty_id = sum(1 for r in rows if not r["entity_id"])
    if empty_id or bad_level:
        checks.append(("entity", "FAIL", f"ENTITY_ID/ENTITY_LEVEL хоосон: {empty_id} мөр"))
    if calc.value_range:
        lo, hi = calc.value_range.get("min"), calc.value_range.get("max")
        bad = sum(1 for r in rows if r["value"] is not None and (
            (lo is not None and r["value"] < lo) or (hi is not None and r["value"] > hi)))
        checks.append(("value_range", "FAIL" if bad else "PASS",
                       f"VALUE: {bad} мөр [{lo}, {hi}]-аас гарсан" if bad else ""))
    return checks


def change_check(new, prev_date, prev, max_pct: float) -> tuple:
    if prev_date is None or prev is None or new is None:
        return "PASS", "Өмнөх үе алга"
    new, prev = float(new), float(prev)
    if prev == 0:
        return ("PASS", f"өмнөх ({prev_date}) 0") if new == 0 else ("WARN", f"өмнөх ({prev_date}) 0, одоо {new:,.4f}")
    pct = (new - prev) / abs(prev) * 100
    msg = f"{prev_date} {prev:,.4f} → {new:,.4f} ({pct:+.1f}%)"
    return ("WARN" if abs(pct) > max_pct else "PASS"), msg


def _id(v) -> str:
    """ENTITY_ID: 101, 101.0, Decimal('101'), ' 101 ' → '101'."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") and s[:-2].isdigit() else s


def _to_rows(cols: list[str], raw: list) -> list[dict]:
    idx = {c: i for i, c in enumerate(cols)}

    def get(r, c, typ="Nullable(Float64)"):
        return convert_value(r[idx[c]], typ) if c in idx else None
    return [{"entity_level": str(r[idx["ENTITY_LEVEL"]] or "").strip().upper(),
             "entity_id": _id(r[idx["ENTITY_ID"]]),
             "entity_name": get(r, "ENTITY_NAME", "Nullable(String)"),
             "metric": str(get(r, "METRIC", "Nullable(String)") or "value").strip().lower(),
             "numerator": get(r, "NUMERATOR"), "denominator": get(r, "DENOMINATOR"),
             "value": get(r, "VALUE"),
             "value_text": get(r, "VALUE_TEXT", "Nullable(String)"),
             "source_row_count": get(r, "SOURCE_ROW_COUNT", "Nullable(Int64)"),
             "data_status": get(r, "DATA_STATUS", "Nullable(String)") or "OK"} for r in raw]


def _source_ready(ctx: RunContext, calc: Indicator, src: Connector, params: dict, timeout: int):
    sql = prep_sql(calc.source_check, ctx.cfg)
    _, rows = src.query(sql, params, timeout)
    value = rows[0][0] if rows and rows[0] else None
    try:
        return bool(value) and float(value) > 0, value
    except (TypeError, ValueError):
        return bool(value), value


def _custom_checks(ctx: RunContext, calc: Indicator, ind: Indicator, conn: Connector, params: dict) -> list:
    """check_sql: ri_result-д бичсэний дараа. {target_table} = riskassessment.ri_result,
    {p_indicator_id:String} = энэ үзүүлэлт. CHECK_NAME, CHECK_STATUS, MESSAGE буцаана."""
    if not calc.check_sql:
        return []
    sql = prep_sql(calc.check_sql, ctx.cfg)
    sql = sql.replace("{target_table}", f"`{ctx.cfg.result_db}`.`{store.RESULT_TABLE}`")
    cols, rows = conn.query(sql, {**params, "p_indicator_id": ind.indicator_id, "p_run_id": ctx.run_id},
                            calc.timeout_seconds)
    need = {"CHECK_NAME", "CHECK_STATUS", "MESSAGE"}
    cols = [c.upper() for c in cols]
    if not need <= set(cols):
        return [("custom_check", "FAIL", f"check_sql нь {sorted(need)} багана буцаах ёстой")]
    i = {c: cols.index(c) for c in need}
    return [(str(r[i["CHECK_NAME"]]), str(r[i["CHECK_STATUS"]]).upper(), str(r[i["MESSAGE"]] or "")) for r in rows]


def _save_csv(ctx: RunContext, calc: Indicator, d: dt.date, rows: list[dict]) -> None:
    folder = OUTPUT_DIR / ctx.cfg.env
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{calc.indicator_id.lower()}_{d:%Y%m%d}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["report_date", *rows[0].keys()])
        w.writeheader()
        w.writerows({"report_date": d, **r} for r in rows)
    log.info("   CSV: %s", path.relative_to(OUTPUT_DIR.parent))


# ── Нэг тооцоолол ажиллуулах ──────────────────────────────────────────────────
def fetch_calc(ctx: "RunContext", calc: Indicator, d: dt.date, start: dt.date,
               target: Indicator | None = None) -> tuple[list[dict], dict]:
    """Тооцооллын SQL-ийг source дээр ЗӨВХӨН уншиж (read_only) мөрүүдийг буцаана — бичихгүй (verify)."""
    params = calc_params(ctx, calc, d, start, target)
    src = ctx.conn(calc.connection, read_only=True)
    try:
        cols, _, raw = src.query_typed(prep_sql(calc.read_sql(), ctx.cfg), params,
                                       calc.timeout_seconds or ctx.cfg.default_timeout)
    finally:
        if ctx.pool is None:
            src.close()
    cols = [c.upper() for c in cols]
    store.check_standard_columns(cols)
    return _to_rows(cols, raw), params


def calc_params(ctx: RunContext, calc: Indicator, d: dt.date, start: dt.date,
                target: Indicator | None = None) -> dict:
    """SQL-ийн параметрүүд: :p_period_start (= :p_date_from), :p_report_date (= :p_date_to), :p_quarters,
    :p_activity_branch_id (нэг үйл ажиллагааны) + тодорхойлолтын ба үзүүлэлтийн params."""
    extra = target.params if target is not None and target is not calc else {}
    params = {**period_params(calc.frequency, d), "p_run_id": ctx.run_id, **calc.params, **extra}
    params["p_period_start"] = start
    params["p_prev_period_end"] = start - dt.timedelta(days=1)
    params["p_quarters"] = quarters_between(start, d)
    owner = calc if not calc.is_calc else target
    act = ctx.cat.activities.get(owner.activity_id) if ctx.cat is not None and owner is not None else None
    if act is not None and act.branch_id:      # энэ үйл ажиллагааны BRANCHID (нийтлэг SQL-д group_by_calc салгана)
        params["p_activity_branch_id"] = act.branch_id
    return with_aliases(params)


def execute_calc(ctx: RunContext, calc: Indicator, targets: list[Indicator], d: dt.date,
                 start: dt.date | None = None) -> list[Outcome]:
    """Тооцооллыг [start, d] хугацаанд НЭГ удаа ажиллуулж, үзүүлэлт бүрийн мөрийг бичнэ. Үзүүлэлт бүрт Outcome."""
    cfg = ctx.cfg
    started = dt.datetime.now()
    if start is None:
        start = period_start_for(ctx, targets[0], ctx.cat.activities.get(targets[0].activity_id), d)[0]
    params = calc_params(ctx, calc, d, start, targets[0])
    outs = {t.indicator_id: Outcome(t, d, "FAILED", started, started, period_start=params["p_period_start"])
            for t in targets}
    timeout = calc.timeout_seconds or cfg.default_timeout
    src = res = None
    try:
        res = ctx.conn(cfg.result_connection)
        src = ctx.conn(calc.connection, read_only=True)         # result-тай ижил ClickHouse байсан ч зөвхөн уншина
        sql = prep_sql(calc.read_sql(), cfg)

        if ctx.mode == "DRY_RUN":
            if is_plsql_block(sql):           # procedure блок: нэг удаа ажиллуулж багана шалгана (READ ONLY)
                probe = sql
            else:
                # Мөр шилжүүлэх нь SQL-ийн сүүлийн "-- comment" хаалтыг дарахаас сэргийлнэ
                probe = (f"SELECT * FROM (\n{sql}\n) WHERE 1 = 0" if src.type == "oracle"
                         else f"SELECT * FROM (\n{sql}\n) LIMIT 0")
            cols, types, _ = src.query_typed(probe, params, timeout)
            store.check_standard_columns(cols)
            info = [("columns", "INFO", ", ".join(f"{c.lower()} {t}" for c, t in zip(cols, types)))]
            if calc.source_check:
                ready, value = _source_ready(ctx, calc, src, params, timeout)
                info.append(("source_check", "INFO" if ready else "WARN",
                             f"source {'бэлэн' if ready else 'БЭЛЭН БИШ'} (={value})"))
            for o in outs.values():
                o.status, o.checks = "DRY_RUN_OK", info
            return list(outs.values())

        # 0. Source бэлэн эсэх (хагас ачаалагдсан датаг оруулахгүй)
        if calc.source_check:
            ready, value = _source_ready(ctx, calc, src, params, timeout)
            if not ready:
                for o in outs.values():
                    o.status, o.error_code = "SKIPPED", "SOURCE_NOT_READY"
                    o.error_message = f"source_check = {value}: {d}-ний source дата бэлэн биш"
                return list(outs.values())

        # 1. SQL-ийг НЭГ удаа
        cols, _, raw = src.query_typed(sql, params, timeout)
        cols = [c.upper() for c in cols]
        store.check_standard_columns(cols)
        rows = _to_rows(cols, raw)
        if ctx.save_csv and rows:
            _save_csv(ctx, calc, d, rows)
        calc_checks = validate_calc(calc, rows)

        # 2. Үзүүлэлт (үйл ажиллагаа) бүрд
        for t in targets:
            _write_target(ctx, calc, t, outs[t.indicator_id], rows, calc_checks, res, params, d)
        return list(outs.values())
    except Exception as exc:  # noqa: BLE001 — нэг тооцооллын алдаа бусдыг зогсоохгүй
        code, msg = classify_error(exc)
        for o in outs.values():
            if o.status in OK_STATUSES or o.status in PROBLEM_STATUSES - {"FAILED"}:
                continue
            o.status = "TIMEOUT" if code == "TIMEOUT" else "FAILED"
            o.error_code, o.error_message = o.error_code or code, o.error_message or msg
        return list(outs.values())
    finally:
        for o in outs.values():
            o.finished_at = dt.datetime.now()
            _audit(ctx, o, res)
        if ctx.pool is None:                 # pool-гүй (шууд дуудсан) бол энд хаана
            for c in (src, res):
                if c is not None:
                    c.close()


def target_rows(ctx: RunContext, calc: Indicator, t: Indicator, rows: list[dict], params: dict, d: dt.date,
                res: Connector | None = None) -> tuple[list[dict], list, dict]:
    """Тооцооллын мөрүүдээс НЭГ үзүүлэлтийн ri_result-ийн мөрүүд: (мөрүүд, шалгалтууд, {value, score, src}).

    ACTIVITY мөр (үйл ажиллагааны утга, оноо, жин, SOLID-ууд) + drill-down (SOL г.м.). run, verify хоёулаа
    ашиглана. res өгвөл max_change_pct-ийг өмнөх үетэй харьцуулна."""
    cfg, act = ctx.cfg, ctx.cat.activities[t.activity_id]
    checks: list = []
    agg, drill, extra = activity_rows(t, act, rows, d, t.rollup_metrics or calc.rollup_metrics)
    checks += extra
    meta: dict = {"value": None, "score": None, "src": None}
    base = {"report_date": d, "period_start": params.get("p_period_start"), "row_type": "INDICATOR",
            "group_no": act.group_no, "activity_id": act.activity_id, "branch_id": str(act.branch_id or ""),
            "activity_name": act.name_mn, "indicator_id": t.indicator_id, "indicator_name": t.name_mn,
            "calc_id": t.calc_id, "source_kind": "SHARED" if t.mode == "shared" else "SQL",
            "score_type": t.score_type, "scale_version": t.scale_version, "file_name": t.file_name,
            "run_id": ctx.run_id, "sql_version": version_of(ctx.cat, t)}
    act_sols = activity_sol_ids(act, d)
    out_rows = []
    primary = t.score_metric if t.score_metric in agg else next(iter(sorted(agg)), None)
    for metric, a in sorted(agg.items()):
        r = dict(base, entity_level="ACTIVITY", entity_id=str(act.branch_id or act.activity_id),
                 primary=metric == primary,           # ri_result-д хадгалагдах мөр (оноо тооцсон METRIC)
                 entity_name=act.name_mn, sol_id=act_sols, metric=metric, numerator=a["numerator"],
                 denominator=a["denominator"], value=a["value"], data_status=a["data_status"],
                 source_row_count=a["source_row_count"],
                 value_text="; ".join(a["value_texts"])[:1000] or None)
        if metric == t.score_metric:
            s, label, st, text = score_value(t, a["value"], a["value_texts"])
            r.update(score=s, score_label=label, weight=t.weight)
            if text:
                r["value_text"] = text
            meta.update(value=a["value"], score=s, src=a["source_row_count"])
            if st == "NO_SCALE":
                checks.append(("scale", "WARN" if t.weight else "INFO", "шатлал тодорхойлогдоогүй — оноонд орохгүй"))
            if t.max_change_pct and res is not None:
                pdate, prev = store.previous_value(cfg, res, t.indicator_id, d, metric)
                checks.append(("max_change_pct", *change_check(a["value"], pdate, prev, t.max_change_pct["pct"])))
        out_rows.append(r)
    if t.score_metric not in agg:
        checks.append(("score_metric", "WARN", f"'{t.score_metric}' METRIC SQL-д алга — оноо тооцогдсонгүй"))
    for dr in drill:
        out_rows.append(dict(base, entity_level=dr["entity_level"], entity_id=dr["entity_id"],
                             entity_name=dr["entity_name"], parent_id=str(act.branch_id or ""),
                             sol_id=dr["entity_id"] if dr["entity_level"] == "SOL" else "",
                             value_text=dr.get("value_text"),
                             metric=dr["metric"], numerator=dr["numerator"], denominator=dr["denominator"],
                             value=dr["value"], data_status=dr["data_status"],
                             source_row_count=dr["source_row_count"]))
    return out_rows, checks, meta


def _write_target(ctx: RunContext, calc: Indicator, t: Indicator, out: Outcome, rows: list[dict],
                  calc_checks: list, res: Connector, params: dict, d: dt.date) -> None:
    cfg, act = ctx.cfg, ctx.cat.activities[t.activity_id]
    if not act.branch_id:
        out.status, out.error_code = "FAILED", "BRANCH_NOT_MAPPED"
        out.error_message = f"{act.activity_id}-д BRANCHID алга (config/activity_map.csv эсвэл activity.yaml branch_id)"
        return
    scope = {"risk_ind_id": t.indicator_id, "snapshot_date": d}
    inserted = False
    try:
        checks = list(calc_checks)
        if not rows:
            failed = any(s == "FAIL" for _, s, _ in checks)
            out.checks, out.status = checks, ("VALIDATION_FAILED" if failed else "WARNING")
            if failed:
                out.error_code, out.error_message = "VALIDATION_FAILED", out.problem_text
            return
        out_rows, extra, meta = target_rows(ctx, calc, t, rows, params, d, res)
        checks += extra
        out.value, out.score, out.source_row_count = meta["value"], meta["score"], meta["src"]
        out.result_row_count = len(out_rows)
        if not out_rows:                     # тооцоолол мөртэй, гэхдээ энэ үйл ажиллагаанд юу ч гараагүй
            out.affected_rows = store.clear_scope(cfg, res, scope, ctx.run_id)
            checks.append(("no_rows", "WARN", "энэ үйл ажиллагаанд мөр гарсангүй" + (
                f" — өмнөх {out.affected_rows} мөрийг ri_history-д шилжүүлэв" if out.affected_rows else "")))
            out.checks, out.status = checks, "WARNING"
            return

        failed_before = any(s == "FAIL" for _, s, _ in checks)
        if not failed_before or cfg.keep_on_validation_fail:
            inserted = True             # insert дунд тасарсан ч except-д цэвэрлэнэ
            store.insert_result_verified(cfg, res, out_rows, scope, ctx.run_id)
            checks.append(("readback", "PASS", f"{len(out_rows)} мөр ClickHouse-оос буцааж уншиж тулгав"))
            checks += _custom_checks(ctx, calc, t, res, params)
            if any(s == "FAIL" for _, s, _ in checks) and not cfg.keep_on_validation_fail:
                store.discard_run(cfg, res, scope, ctx.run_id)
                checks.append(("rollback", "INFO", "Шалгалт унасан тул шинэ мөрийг устгав, хуучин өгөгдөл үлдэв"))
            else:
                with _REPLACED_LOCK:
                    ctx.replaced.append((t.indicator_id, d))   # хуучин мөрийг тайлант өдрийн төгсгөлд НЭГ DELETE-ээр
            inserted = False
        failed = any(s == "FAIL" for _, s, _ in checks)
        out.checks = checks
        out.status = "VALIDATION_FAILED" if failed else (
            "WARNING" if any(s == "WARN" for _, s, _ in checks) else "SUCCESS")
        if failed:
            out.error_code, out.error_message = "VALIDATION_FAILED", out.problem_text
    except Exception as exc:  # noqa: BLE001
        code, msg = classify_error(exc)
        out.status = "TIMEOUT" if code == "TIMEOUT" else "FAILED"
        out.error_code, out.error_message = code, msg
        if inserted:
            try:
                store.discard_run(cfg, res, scope, ctx.run_id)
                out.error_message = f"[шинэ мөрийг буцааж устгав, хуучин өгөгдөл хэвээр] {msg}"
            except Exception as cleanup_exc:  # noqa: BLE001
                out.error_message = f"[АНХААР: шинэ мөрийг устгаж чадсангүй — run_id={ctx.run_id}: {cleanup_exc}] {msg}"


# ── Үйл ажиллагааны нийт оноо ─────────────────────────────────────────────────
def aggregate_activity(cfg: EnvConfig, cat: Catalog, conn: Connector, activity_id: str, d: dt.date,
                       run_id: str) -> dict:
    """ACTIVITY мөр: Σ(жин × оноо) / Σ(оноотой үзүүлэлтийн жин) — DaHUB-ийн арга. Үр дүнг буцаана."""
    act = cat.activities[activity_id]
    if not act.branch_id:
        raise RunnerError("BRANCH_NOT_MAPPED", f"{activity_id}-д BRANCHID алга (config/activity_map.csv)")
    scoring = load_scoring(cfg)
    high, medium = scoring["high"], scoring["medium"]
    inds = [i for i in cat.by_activity(activity_id) if i.enabled and not i.example and i.weight]
    total_w = sum(i.weight or 0 for i in inds)
    scored = activity_scored(cat, activity_id, store.activity_inputs(cfg, conn, act.branch_id, d))
    sw = sum(w for _, _, w in scored)
    value = sum(s * w for _, s, w in scored) / sw if sw else None
    lvl = risk_level(value, high, medium)
    row = {"report_date": d, "row_type": "ACTIVITY", "activity_id": activity_id,
           "branch_id": str(act.branch_id or ""), "activity_name": act.name_mn,
           "sol_id": activity_sol_ids(act, d), "value": value, "level": lvl, "run_id": run_id}
    scope = {"branch_id": str(act.branch_id), "risk_ind_id": store.TOTAL_ID, "snapshot_date": d}
    store.insert_result_verified(cfg, conn, [row], scope, run_id)
    store.keep_only_run(cfg, conn, scope, run_id)
    return {"activity_id": activity_id, "branch_id": act.branch_id, "report_date": d, "value": value, "level": lvl,
            "n_scored": len(scored), "n_indicators": len(inds), "coverage": (sw / total_w) if total_w else None,
            "total_weight": total_w}


def activity_scored(cat: Catalog, activity_id: str, inputs: list[tuple]) -> list[tuple]:
    """[(risk_ind_id, оноо)] (ri_result) → [(id, оноо, жин)]: оноотой (> 0), энэ үйл ажиллагааны, жинтэй үзүүлэлт.
    Жин нь activities/-аас (ri_result-д хадгалахгүй)."""
    out = []
    for iid, s in inputs:
        ind = cat.indicators.get(iid)
        if ind is None or ind.activity_id != activity_id or not ind.enabled or ind.example or not ind.weight:
            continue
        if s is not None and s > 0:
            out.append((iid, float(s), float(ind.weight)))
    return out


def refresh_activities(cfg: EnvConfig, cat: Catalog, activity_ids, d: dt.date, run_id: str) -> list[dict]:
    out = []
    with connect(cfg, cfg.result_connection) as conn:
        for aid in sorted(set(activity_ids)):
            try:
                out.append(aggregate_activity(cfg, cat, conn, aid, d, run_id))
            except Exception as exc:  # noqa: BLE001
                log.warning("%s %s нийт оноо тооцож чадсангүй: %s", aid, d, exc)
    return out


# ── Audit, лог ────────────────────────────────────────────────────────────────
def _audit_rec(ctx: RunContext, out: Outcome) -> dict:
    ind = out.indicator
    return {
        "RUN_ID": ctx.run_id, "RUN_MODE": ctx.mode, "ACTIVITY_ID": ind.activity_id,
        "INDICATOR_ID": ind.indicator_id, "REPORT_DATE": out.report_date,
        "PERIOD_START": out.period_start, "EXECUTION_STATUS": out.status, "STARTED_AT": out.started_at,
        "FINISHED_AT": out.finished_at, "DURATION_SECONDS": out.duration,
        "AFFECTED_ROWS": out.affected_rows, "SOURCE_ROW_COUNT": out.source_row_count,
        "RESULT_ROW_COUNT": out.result_row_count, "VALIDATION_DETAIL": out.check_text or None,
        "ERROR_CODE": out.error_code, "ERROR_MESSAGE": out.error_message,
        "EXECUTED_BY": ctx.executed_by, "ENVIRONMENT": ctx.cfg.env,
        "SQL_VERSION": version_of(ctx.cat, ind) if ctx.cat else ind.sql_version, "CONNECTION_NAME": ind.connection,
        "TARGET_TABLE": store.RESULT_TABLE,
    }


def _audit_fallback(recs: list[dict], exc: Exception) -> None:
    path = LOGS_DIR / f"{dt.date.today():%Y-%m-%d}" / "audit_fallback.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for rec in recs:
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
    log.warning("   audit DB-д бичиж чадсангүй (%s) → %s", exc, path)


def _audit(ctx: RunContext, out: Outcome, conn: Connector | None):
    rec = _audit_rec(ctx, out)
    _log_outcome(out)
    try:
        if conn is None:
            with connect(ctx.cfg, ctx.cfg.result_connection) as c:
                store.write_audit(ctx.cfg, c, rec)
        else:
            store.write_audit(ctx.cfg, conn, rec)
    except Exception as exc:  # noqa: BLE001
        _audit_fallback([rec], exc)


def _log_outcome(out: Outcome) -> None:
    ind = out.indicator
    val = "" if out.value is None else f" value={out.value:.4g}"
    sc = "" if out.score is None else f" score={out.score:g}"
    line = f"{ind.indicator_id} {out.report_date} {out.status:<17} {out.duration:>6.1f}s{val}{sc}"
    if out.status == "DRY_RUN_OK":
        log.info("%s  %s", line, out.check_text[:500])
    elif out.status in OK_STATUSES and out.status != "WARNING":
        log.info(line)
    else:
        log.warning("%s  %s", line, (out.error_message or out.problem_text or "")[:300])


# ── Олон тооцоолол, огноо ─────────────────────────────────────────────────────
def _skip(ctx: RunContext, ind: Indicator, d: dt.date, code: str, reason: str) -> Outcome:
    now = dt.datetime.now()
    out = Outcome(ind, d, "SKIPPED", now, now, error_code=code, error_message=reason)
    _audit(ctx, out, None)
    return out


def _skip_selected(ctx: RunContext, skipped: list, d: dt.date) -> list[Outcome]:
    """Сонголтоор алгассан (status, disabled, metadata алдаа) үзүүлэлтүүд: НЭГ insert, лог дээр хураангуй."""
    if not skipped:
        return []
    now = dt.datetime.now()
    outs = [Outcome(ind, d, "SKIPPED", now, now, error_code=code, error_message=reason)
            for ind, code, reason in skipped]
    by_code: dict[str, int] = {}
    for o in outs:
        by_code[o.error_code] = by_code.get(o.error_code, 0) + 1
        if o.error_code == "INVALID_METADATA":
            _log_outcome(o)
    log.info("%s: алгассан %s", d, ", ".join(f"{k}={v}" for k, v in sorted(by_code.items())))
    recs = [_audit_rec(ctx, o) for o in outs]
    try:
        with connect(ctx.cfg, ctx.cfg.result_connection) as conn:
            store.write_audits(ctx.cfg, conn, recs)
    except Exception as exc:  # noqa: BLE001
        _audit_fallback(recs, exc)
    return outs


def run_date(ctx: RunContext, targets: list[Indicator], d: dt.date) -> list[Outcome]:
    """Нэг тайлант өдөр: тооцоолол × хугацаа бүрийг dependency дарааллаар (зэрэг) нэг удаа ажиллуулна."""
    groups = group_by_calc(ctx, targets, d)
    keys_of: dict[str, set] = {}                    # indicator / calc id → бүлгийн түлхүүрүүд
    for key, (calc, _, tg) in groups.items():
        keys_of.setdefault(calc.indicator_id, set()).add(key)
        for t in tg:
            keys_of.setdefault(t.indicator_id, set()).add(key)

    def deps_of(key: str) -> set:
        calc, _, tg = groups[key]
        deps = set(calc.dependencies) | {x for t in tg for x in t.dependencies}
        return {k for x in deps for k in keys_of.get(x, ())} - {key}

    ts = TopologicalSorter({key: deps_of(key) for key in groups})
    try:
        ts.prepare()
    except CycleError as exc:                       # select() барьдаг; энд хүрвэл run-ийг унагахгүй
        cyc = set(exc.args[1])
        out = [_skip(ctx, t, d, "DEPENDENCY_CYCLE", f"dependency тойрог: {' -> '.join(exc.args[1])}")
               for k in cyc for t in groups[k][2]]
        rest = [t for k, (_, _, tg) in groups.items() if k not in cyc for t in tg]
        return out + (run_date(ctx, rest, d) if rest else [])
    results: dict[str, list[Outcome]] = {}
    with ThreadPoolExecutor(max_workers=max(1, ctx.workers)) as pool:
        running = {}
        while ts.is_active():
            for key in sorted(ts.get_ready(), key=lambda k: (groups[k][0].execution_order, k)):
                calc, start, tgts = groups[key]
                bad = next((x for x in sorted(deps_of(key)) if x in results
                            and any(o.status not in OK_STATUSES for o in results[x])), None)
                if bad:
                    results[key] = [_skip(ctx, t, d, "DEPENDENCY_FAILED", f"{bad.split('@')[0]} амжилтгүй")
                                    for t in tgts]
                    ts.done(key)
                elif ctx.cfg.enforce_frequency and not ctx.force and not is_due(calc.frequency, d):
                    results[key] = [_skip(ctx, t, d, "NOT_DUE", f"{calc.frequency} үзүүлэлт {d}-нд ажиллахгүй")
                                    for t in tgts]
                    ts.done(key)
                else:
                    dep_ids = {t.indicator_id for k2 in deps_of(key) for t in groups[k2][2]}
                    if dep_ids:                 # ri_result-аас уншдаг бол dependency-ийн хуучин мөрийг эхлээд устгана
                        _replace_old(ctx, d, dep_ids)
                    running[pool.submit(execute_calc, ctx, calc, tgts, d, start)] = key
            if not running:
                continue
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for fut in finished:
                key = running.pop(fut)
                results[key] = fut.result()
                ts.done(key)
    _replace_old(ctx, d)
    return [o for outs in results.values() for o in outs]


def _replace_old(ctx: RunContext, d: dt.date, only: set | None = None) -> None:
    """Энэ өдөр бичсэн үзүүлэлтүүдийн ХУУЧИН мөрийг ri_history-д хуулж НЭГ DELETE-ээр устгана (үзүүлэлт бүрт
    тусдаа DELETE хийхэд ClickHouse-ийн mutation олширч удаашрах, зэрэг ажиллахад мөр үлдэх эрсдэлтэй).
    only: зөвхөн эдгээр үзүүлэлт (dependency-тэй тооцоолол эхлэхээс өмнө)."""
    with _REPLACED_LOCK:
        pairs = [p for p in ctx.replaced if p[1] == d and (only is None or p[0] in only)]
        ctx.replaced[:] = [p for p in ctx.replaced if p not in set(pairs)]
    if not pairs or ctx.mode == "DRY_RUN":
        return
    try:
        with connect(ctx.cfg, ctx.cfg.result_connection) as conn:
            n = store.keep_only_run_many(ctx.cfg, conn, pairs, ctx.run_id)
        log.info("%s: %s үзүүлэлтийн хуучин %s мөрийг ri_history-д шилжүүлэв", d, len(pairs), n)
    except Exception as exc:  # noqa: BLE001 — шинэ мөр зөв бичигдсэн; хуучин нь үлдвэл verify барина, дараагийн run арилгана
        log.error("%s: хуучин мөрийг устгаж чадсангүй (%s) — python ri.py verify, дахин run", d, exc)
        ctx.replace_failed = True


def sync_meta(cfg: EnvConfig, cat: Catalog) -> None:
    """ri_activity, ri_indicator (UI-ийн лавлах)-ийг activities/-тай ижил болгоно."""
    try:
        with connect(cfg, cfg.result_connection) as conn:
            na, ni = store.sync_meta(cfg, conn, cat, load_scoring(cfg)["groups"])
        log.info("Лавлах синк: %s үйл ажиллагаа, %s үзүүлэлт", na, ni)
    except Exception as exc:  # noqa: BLE001 — лавлах синк унасан ч тооцоолол үргэлжилнэ
        log.warning("Лавлах (ri_activity, ri_indicator) синк хийж чадсангүй: %s", exc)


def run_plan(ctx: RunContext, plan: dict[dt.date, list[Indicator]],
             skipped: list[tuple[Indicator, str, str]]) -> list[Outcome]:
    orgmap.use(ctx.cfg)
    if ctx.pool is None:
        ctx.pool = ConnectionPool(ctx.cfg)
    log.info("RUN %s | env=%s | mode=%s | workers=%s", ctx.run_id, ctx.cfg.env, ctx.mode, ctx.workers)
    started = time.time()
    results: list[Outcome] = []
    activities = []
    if ctx.mode != "DRY_RUN":
        sync_meta(ctx.cfg, ctx.cat)
    for d in sorted(plan):
        results += _skip_selected(ctx, skipped, d)
        if plan[d]:
            outs = run_date(ctx, plan[d], d)
            results.extend(outs)
            if ctx.mode != "DRY_RUN":
                touched = {o.indicator.activity_id for o in outs if o.status in ("SUCCESS", "WARNING")
                           and not o.indicator.example}          # жишээ үйл ажиллагаа нийт оноонд орохгүй
                activities += refresh_activities(ctx.cfg, ctx.cat, touched, d, ctx.run_id)
    ctx.pool.close()
    print_summary(ctx, results, time.time() - started, activities)
    return results


def print_activity_scores(activities: list[dict]) -> None:
    if not activities:
        return
    print("\nҮЙЛ АЖИЛЛАГААНЫ ОНОО  (Σжин×оноо / Σоноотой жин):")
    for a in activities:
        v = "—" if a["value"] is None else f"{a['value']:.2f}"
        cov = "—" if a["coverage"] is None else f"{a['coverage'] * 100:.0f}%"
        warn = "" if abs((a["total_weight"] or 0) - 100) < 0.01 else f"  ⚠ Σжин={a['total_weight']:g}% (100 биш)"
        print(f"  {a['branch_id']:>5} {a['activity_id']} {a['report_date']}  {v:>5} {a['level'] or '—':<6} "
              f"оноотой {a['n_scored']}/{a['n_indicators']}  жингийн хамралт {cov}{warn}")


def print_summary(ctx: RunContext, results: list[Outcome], seconds: float, activities=None) -> None:
    order = ["SUCCESS", "WARNING", "DRY_RUN_OK", "VALIDATION_FAILED", "FAILED", "TIMEOUT", "SKIPPED"]
    by_act: dict[str, dict[str, int]] = {}
    for r in results:
        by_act.setdefault(r.indicator.activity_id, {}).setdefault(r.status, 0)
        by_act[r.indicator.activity_id][r.status] += 1
    used = [s for s in order if any(s in v for v in by_act.values())]
    print()
    print(f"RUN {ctx.run_id}  env={ctx.cfg.env}  mode={ctx.mode}  хугацаа={seconds:.1f}s")
    header = f"{'activity':<10}{'total':>7}" + "".join(f"{s[:12]:>14}" for s in used)
    print(header)
    print("-" * len(header))
    totals = {s: 0 for s in used}
    for act in sorted(by_act):
        row = by_act[act]
        print(f"{act:<10}{sum(row.values()):>7}" + "".join(f"{row.get(s, 0):>14}" for s in used))
        for s in used:
            totals[s] += row.get(s, 0)
    print("-" * len(header))
    print(f"{'TOTAL':<10}{len(results):>7}" + "".join(f"{totals[s]:>14}" for s in used))
    print_activity_scores(activities or [])

    bad = [r for r in results if r.status in PROBLEM_STATUSES]
    if bad:
        print("\nАЛДААТАЙ:")
        for r in bad:
            print(f"  {r.indicator.indicator_id} {r.report_date} {r.status} [{r.error_code}] {(r.error_message or '')[:200]}")
        print(f"\nДахин ажиллуулах:  python ri.py retry --env {ctx.cfg.env} --run-id {ctx.run_id}")
    not_ready = [r for r in results if r.error_code == "SOURCE_NOT_READY"]
    if not_ready:
        print("\nSOURCE БЭЛЭН БИШ (дата ачаалагдсаны дараа retry хийнэ):")
        for r in not_ready:
            print(f"  {r.indicator.indicator_id} {r.report_date} {r.error_message}")
        if not bad:
            print(f"\nДахин ажиллуулах:  python ri.py retry --env {ctx.cfg.env} --run-id {ctx.run_id}")
    warn = [r for r in results if r.status == "WARNING"]
    if warn:
        print("\nАНХААРУУЛГА:")
        for r in warn:
            print(f"  {r.indicator.indicator_id} {r.report_date} {r.problem_text[:200]}")
