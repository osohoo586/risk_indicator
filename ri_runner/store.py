"""ClickHouse: НЭГ үр дүнгийн хүснэгт (risk_assessment.ri_result) + audit + history.

ri_result-ийн мөр = үзүүлэлт × үйл ажиллагаа (BRANCHID) × тайлант өдөр:
  activity, activity_id, solid (SOLID-ууд, metadata), branch_id, risk_indicator, risk_ind_id,
  result_number (тооцсон утга), result (оноо; TOTAL мөрөнд түвшин), snapshot_date (+ техникийн run_id, loaded_at).
Runner дотроо SOL задаргаа, тоологч / хуваарьтай мөрүүдээр тооцно (verify, --save-csv); `to_result_rows` нь тэднийг
ri_result-ийн мөр болгоно.

Бичих нэгж (scope):
  үзүүлэлт  — (risk_ind_id, snapshot_date)
  нийт оноо — (branch_id, risk_ind_id='TOTAL', snapshot_date)   (1 BRANCHID = 1 үйл ажиллагаа)

Бичих: шинэ мөрийг run_id-тай бичээд ClickHouse-оос БУЦААЖ уншиж мөр бүрийг тулгана (insert_result_verified) —
зөрвөл энэ run-ий мөрийг устгаад алдаа (FAILED, хуучин утга хэвээр).
Дахин ажиллуулах: шинэ мөрийг run_id-тай бичээд, шалгалт давбал тухайн scope-ийн хуучин мөрүүдийг
ri_history-д (JSON) хуулж устгана. Зэрэг ажилласан run-уудаас хамгийн сүүлд бичсэн нь үлдэнэ.
Шалгалт унавал (prod) шинэ мөрийг устгаж хуучин нь үлдэнэ.
"""
import datetime as dt
import logging
import math
import re
import threading
import time

from .config import DDL_DIR, EnvConfig
from .db import Connector, RunnerError

# ClickHouse-ийн lightweight DELETE олон thread-ээс зэрэг ажиллахад хуучин мөр ховор тохиолдолд үлдсэн (25.8,
# demo_check-ийн verify барьсан) → DELETE-ийг process дотор дараалуулж, дараа нь үлдсэн эсэхийг заавал шалгана.
_DELETE_LOCK = threading.Lock()
DELETE_RETRIES = 3

RESULT_TABLE = "ri_result"
ACTIVITY_TABLE = "ri_activity"
INDICATOR_TABLE = "ri_indicator"
VIEWS = ("v_activity_score", "v_indicator_score")
OLD_VIEWS = ("v_indicator_detail", "v_risk_indicators")        # хуучин бүтцийнх — init-db устгана
AUDIT_TABLE = "ri_execution_audit"
HISTORY_TABLE = "ri_history"

TOTAL_ID = "TOTAL"                                # үйл ажиллагааны нийт оноо (risk_ind_id)
TOTAL_NAME = "Нийт оноо"
RESULT_COLUMNS = ("activity", "activity_id", "solid", "branch_id", "risk_indicator", "risk_ind_id",
                  "result_number", "result", "snapshot_date", "run_id")
AUDIT_COLUMNS = ("run_id", "run_mode", "activity_id", "indicator_id", "report_date", "period_start",
                 "execution_status", "started_at", "finished_at", "duration_seconds",
                 "affected_rows", "source_row_count", "result_row_count", "validation_detail",
                 "error_code", "error_message", "executed_by", "environment", "sql_version",
                 "connection_name", "target_table")

# SQL-ийн стандарт багана
STD_REQUIRED = ("ENTITY_LEVEL", "ENTITY_ID", "VALUE")
STD_OPTIONAL = ("ENTITY_NAME", "METRIC", "NUMERATOR", "DENOMINATOR", "VALUE_TEXT", "SOURCE_ROW_COUNT",
                "DATA_STATUS")


def q(name: str) -> str:
    return f"`{name}`"


def check_standard_columns(cols: list[str]) -> None:
    missing = [c for c in STD_REQUIRED if c not in cols]
    extra = [c for c in cols if c not in STD_REQUIRED + STD_OPTIONAL]
    dup = sorted({c for c in cols if cols.count(c) > 1})
    if missing or extra or dup:
        raise RunnerError("OUTPUT_SCHEMA",
                          f"SQL нь стандарт багана буцаах ёстой: заавал {list(STD_REQUIRED)}, "
                          f"сонголтоор {list(STD_OPTIONAL)}. Дутуу {missing}, илүү {extra}, давхар {dup}")


# ── Хүснэгтүүд ────────────────────────────────────────────────────────────────
def _run_ddl(cfg: EnvConfig, conn: Connector, file: str) -> None:
    ddl = (DDL_DIR / "clickhouse" / file).read_text(encoding="utf-8")
    ddl = "\n".join(l for l in ddl.splitlines() if not l.strip().startswith("--"))
    conn.execute(ddl.replace("{db}", cfg.result_db).strip().rstrip(";"))


def ensure_base(cfg: EnvConfig, conn: Connector, log=print) -> bool:
    """database, ri_result, audit, history-г (байхгүй бол) үүсгэнэ."""
    _, rows = conn.query("SELECT count() FROM system.databases WHERE name = {d:String}", {"d": cfg.result_db})
    if not rows[0][0]:
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {q(cfg.result_db)}")
    created = False
    if conn.table_exists(cfg.result_db, RESULT_TABLE) and \
            "risk_ind_id" not in set(conn.table_columns(cfg.result_db, RESULT_TABLE)):
        legacy = f"{RESULT_TABLE}_legacy_{dt.datetime.now():%Y%m%d%H%M%S}"   # хуучин бүтэц: устгахгүй, нэрийг нь солино
        conn.execute(f"RENAME TABLE {q(cfg.result_db)}.{RESULT_TABLE} TO {q(cfg.result_db)}.{q(legacy)}")
        log(f"Хуучин бүтэцтэй {cfg.result_db}.{RESULT_TABLE}-ийг {legacy} нэрээр хадгаллаа (устгаагүй)")
    for table, file in ((RESULT_TABLE, "ri_result.sql"), (HISTORY_TABLE, "ri_history.sql"),
                        (AUDIT_TABLE, "ri_execution_audit.sql"), (ACTIVITY_TABLE, "ri_activity.sql"),
                        (INDICATOR_TABLE, "ri_indicator.sql")):
        if not conn.table_exists(cfg.result_db, table):
            _run_ddl(cfg, conn, file)
            log(f"Хүснэгт үүсгэлээ: {cfg.result_db}.{table}")
            created = True
    existing = set(conn.table_columns(cfg.result_db, AUDIT_TABLE))
    if "period_start" not in existing:
        conn.execute(f"ALTER TABLE {q(cfg.result_db)}.{AUDIT_TABLE} "
                     f"ADD COLUMN IF NOT EXISTS period_start Nullable(Date) AFTER report_date")
    if created or not all(conn.table_exists(cfg.result_db, v) for v in VIEWS):
        ensure_views(cfg, conn)
        log(f"View: {', '.join(VIEWS)}")
    return created


def ensure_views(cfg: EnvConfig, conn: Connector) -> None:
    """UI-д зориулсан view-уудыг (CREATE OR REPLACE) үүсгэнэ — ddl/clickhouse/views.sql."""
    text = (DDL_DIR / "clickhouse" / "views.sql").read_text(encoding="utf-8")
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    for v in OLD_VIEWS:
        conn.execute(f"DROP VIEW IF EXISTS {q(cfg.result_db)}.{v}")
    for stmt in (s.strip() for s in text.split(";")):
        if stmt:
            conn.execute(stmt.replace("{db}", cfg.result_db))


# ── Лавлах хүснэгт (UI): activities/-аас синк ────────────────────────────────
ACTIVITY_META_COLUMNS = ("branch_id", "activity_id", "group_no", "activity_name", "activity_name_old",
                         "n_indicators", "total_weight", "is_active")
INDICATOR_META_COLUMNS = ("indicator_id", "indicator_no", "sort_order", "branch_id", "activity_id", "group_no",
                          "indicator_name", "score_group", "score_group_name", "weight", "mode", "calc_id",
                          "status", "frequency", "value_unit", "scale_text", "scale_json", "source_system",
                          "required_info", "method", "period_text", "owner", "is_active")


def sync_meta(cfg: EnvConfig, conn: Connector, cat, group_names: dict | None = None) -> tuple[int, int]:
    """ri_activity, ri_indicator-ийг catalog-тай ижил болгоно. Устгагдсан нь is_active = 0."""
    import json
    group_names = group_names or {}
    acts = [a for a in cat.activities.values() if a.branch_id and not a.example]
    a_rows, i_rows = [], []
    for a in acts:
        inds = [i for i in cat.by_activity(a.activity_id) if i.enabled]
        a_rows.append([a.branch_id, a.activity_id, a.group_no, a.name_mn, a.name_old, len(inds),
                       float(sum(i.weight or 0 for i in inds)), 1])
        for i in inds:
            g = (i.score_type or "").lower()
            i_rows.append([i.indicator_id, i.indicator_no, i.sort_order, a.branch_id, a.activity_id, a.group_no,
                           i.name_mn, g, group_names.get(g, ""), i.weight, i.mode, i.calc_id, i.status, i.frequency,
                           i.value_unit, i.scale_text.strip(),
                           json.dumps(i.scale, ensure_ascii=False) if i.scale else "",
                           str(i.master.get("source_system") or ""), str(i.master.get("required_info") or ""),
                           str(i.master.get("method") or ""), str(i.master.get("period_text") or ""), i.owner, 1])
    db = q(cfg.result_db)
    for table, key, rows, cols in ((ACTIVITY_TABLE, "branch_id", a_rows, ACTIVITY_META_COLUMNS),
                                   (INDICATOR_TABLE, "indicator_id", i_rows, INDICATOR_META_COLUMNS)):
        if rows:
            conn.insert(cfg.result_db, table, list(cols), rows)
        keep = [r[0] for r in rows] or [""]
        conn.execute(f"INSERT INTO {db}.{table} SELECT * REPLACE (0 AS is_active, now64(3) AS synced_at) "
                     f"FROM {db}.{table} FINAL WHERE is_active = 1 AND {key} NOT IN {{k:Array(String)}}", {"k": keep})
    return len(a_rows), len(i_rows)


def _audit_row(rec: dict) -> list:
    rec = {k.lower(): v for k, v in rec.items()}
    row = []
    for c in AUDIT_COLUMNS:
        v = rec.get(c)
        if c in ("error_message", "validation_detail") and v:
            v = str(v)[:4000]
        row.append(v)
    return row


def write_audit(cfg: EnvConfig, conn: Connector, rec: dict) -> None:
    conn.insert(cfg.result_db, AUDIT_TABLE, list(AUDIT_COLUMNS), [_audit_row(rec)])


def write_audits(cfg: EnvConfig, conn: Connector, recs: list[dict]) -> None:
    """Олон бүртгэлийг НЭГ insert-ээр (жнь prod-д алгассан 1,000+ үзүүлэлт)."""
    if recs:
        conn.insert(cfg.result_db, AUDIT_TABLE, list(AUDIT_COLUMNS), [_audit_row(r) for r in recs])


# ── ri_result бичих ───────────────────────────────────────────────────────────
def fmt_score(score) -> str | None:
    """Оноо → ri_result.result: 5.0 → "5", 3.5 → "3.5", None → None (үнэлэхгүй)."""
    if score is None:
        return None
    f = float(score)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def to_result_rows(rows: list[dict]) -> list[dict]:
    """Runner-ийн дотоод мөрүүд → ri_result-ийн мөр (үзүүлэлт × үйл ажиллагаа × өдөрт НЭГ).

    Дотоод мөр: row_type INDICATOR (entity_level ACTIVITY = үйл ажиллагааны утга, SOL г.м. = задаргаа) эсвэл
    ACTIVITY (нийт оноо). Хадгалах нь: үйл ажиллагааны утга (оноо тооцсон METRIC — primary) ба нийт оноо;
    задаргаа, бусад METRIC хадгалагдахгүй."""
    out = []
    for r in rows:
        if r.get("row_type") == "ACTIVITY":
            iid, name, result = TOTAL_ID, TOTAL_NAME, (r.get("level") or None)
        elif r.get("entity_level") == "ACTIVITY" and r.get("primary", True):
            iid, name, result = r.get("indicator_id") or "", r.get("indicator_name") or "", fmt_score(r.get("score"))
        else:
            continue
        out.append({"activity": r.get("activity_name") or "", "activity_id": r.get("activity_id") or "",
                    "solid": r.get("sol_id") or "", "branch_id": str(r.get("branch_id") or ""),
                    "risk_indicator": name, "risk_ind_id": iid, "result_number": r.get("value"),
                    "result": result, "snapshot_date": r.get("report_date"), "run_id": r.get("run_id") or ""})
    return out


def insert_result(cfg: EnvConfig, conn: Connector, rows: list[dict]) -> list[dict]:
    """Дотоод мөрүүдийг ri_result-д бичнэ; бичсэн (хөрвүүлсэн) мөрүүдийг буцаана."""
    out = to_result_rows(rows)
    if out:
        conn.insert(cfg.result_db, RESULT_TABLE, list(RESULT_COLUMNS), [[r[c] for c in RESULT_COLUMNS] for r in out])
    return out


# Буцааж уншиж тулгах түлхүүр, утгын баганууд
_KEY = ("risk_ind_id", "branch_id", "snapshot_date")
_CHECK = ("activity", "activity_id", "solid", "risk_indicator", "result_number", "result")


def _same(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None:
            return a is None and b is None
        return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)
    return (a if a not in ("", None) else None) == (b if b not in ("", None) else None)


def written_diff(sent: list[dict], got: list[dict]) -> list[str]:
    """Илгээсэн мөр ↔ ClickHouse-оос буцааж уншсан мөр: зөрүү бүрийн тайлбар (хоосон = яг таарсан)."""
    def key(r):
        return tuple(str(r.get(k) or "") for k in _KEY)
    have: dict = {}
    for r in got:
        have.setdefault(key(r), []).append(r)
    problems = []
    for r in sent:
        rows = have.pop(key(r), [])
        k = f"{r.get('risk_ind_id')} {r.get('branch_id')} {r.get('snapshot_date')}"
        if not rows:
            problems.append(f"{k}: ClickHouse-д алга")
            continue
        if len(rows) > 1:
            problems.append(f"{k}: {len(rows)} удаа бичигдсэн")
        diff = [f"{c} {r.get(c)!r} ≠ {rows[0].get(c)!r}" for c in _CHECK if c in r and not _same(r.get(c), rows[0].get(c))]
        if diff:
            problems.append(f"{k}: " + ", ".join(diff[:3]))
    problems += [f"{k[0]} {k[1]} {k[2]}: илүү мөр ({len(v)})" for k, v in have.items()]
    return problems


def insert_result_verified(cfg: EnvConfig, conn: Connector, rows: list[dict], scope: dict, run_id: str) -> None:
    """Бичээд ClickHouse-оос буцааж уншиж мөр бүрийг тулгана. Зөрвөл энэ run-ий мөрийг устгаад RunnerError
    (INSERT_MISMATCH) — бүгд зөв бичигдсэн, эсвэл юу ч үлдэхгүй (хуучин утга хэвээр)."""
    sent = insert_result(cfg, conn, rows)
    sw, params = _scope_where(scope)
    params["r"] = run_id
    cols = list(dict.fromkeys(_KEY + _CHECK))
    _, got = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                        f"WHERE {sw} AND run_id = {{r:String}}", params)
    problems = written_diff([{c: r.get(c) for c in cols} for r in sent], [dict(zip(cols, g)) for g in got])
    if problems:
        try:
            discard_run(cfg, conn, scope, run_id)
            note = "бичсэн мөрийг устгав (өмнөх утга хэвээр)"
        except Exception as exc:  # noqa: BLE001
            note = f"устгаж чадсангүй ({exc}) — python ri.py clean"
        raise RunnerError("INSERT_MISMATCH", f"Бичсэн мөр буцааж уншихад зөрлөө ({len(problems)}): "
                                             + "; ".join(problems[:4]) + f" → {note}")


def delete_verified(conn: Connector, table: str, where: str, params: dict, what: str) -> None:
    """DELETE → тэр нөхцөлөөр дахин тоолно; үлдсэн бол дахин (DELETE_RETRIES). Бүтэхгүй бол RunnerError
    (DELETE_INCOMPLETE) — давхардсан мөр чимээгүй үлдэхгүй."""
    left = 0
    for attempt in range(DELETE_RETRIES):
        with _DELETE_LOCK:
            conn.execute(f"DELETE FROM {table} WHERE {where}", params)
        _, rows = conn.query(f"SELECT count() FROM {table} WHERE {where}", params)
        left = int(rows[0][0])
        if not left:
            return
        logging.getLogger("ri").warning("   %s: DELETE-ийн дараа %s мөр үлдсэн — дахин (%s)", what, left, attempt + 2)
        time.sleep(0.3 * (attempt + 1))
    raise RunnerError("DELETE_INCOMPLETE", f"{what}: DELETE-ийн дараа {left} мөр ClickHouse-д үлдлээ "
                                           f"({DELETE_RETRIES} оролдлого)")


def _scope_where(scope: dict) -> tuple[str, dict]:
    parts, params = [], {}
    for k, v in scope.items():
        if not re.fullmatch(r"[a-z_]+", k):
            raise ValueError(k)
        parts.append(f"{k} = {{s_{k}:{'Date' if k == 'snapshot_date' else 'String'}}}")
        params[f"s_{k}"] = v
    return " AND ".join(parts) or "1 = 1", params


# ri_history.indicator_id: үзүүлэлт, эсвэл нийт оноо бол TOTAL_<BRANCHID>
_HIST_SELECT = (f"SELECT if(risk_ind_id = '{TOTAL_ID}', concat('{TOTAL_ID}_', branch_id), risk_ind_id), "
                f"'{RESULT_TABLE}', snapshot_date, run_id, {{r:String}}, formatRowNoNewline('JSONEachRow', *)")
_HIST_INSERT = "(indicator_id, table_name, report_date, run_id, replaced_by_run, row_json)"


def keep_only_run(cfg: EnvConfig, conn: Connector, scope: dict, run_id: str) -> int:
    """scope-ийн хуучин мөрүүдийг ri_history-д хуулаад устгана.

    Зөвхөн ЭНЭ run-ий мөрөөс ӨМНӨ бичигдсэн мөрийг (ижил цагтай бол run_id бага нь) устгана —
    зэрэг run-уудаас хамгийн сүүлд бичсэн нэг нь үлдэнэ.
    """
    db, t = q(cfg.result_db), RESULT_TABLE
    sw, params = _scope_where(scope)
    params["r"] = run_id
    _, rows = conn.query(f"SELECT min(loaded_at) FROM {db}.{t} WHERE {sw} AND run_id = {{r:String}}", params)
    params["mine"] = rows[0][0]
    where = (f"{sw} AND run_id != {{r:String}} AND (loaded_at < {{mine:DateTime64(3)}} "
             f"OR (loaded_at = {{mine:DateTime64(3)}} AND run_id < {{r:String}}))")
    _, rows = conn.query(f"SELECT count() FROM {db}.{t} WHERE {where}", params)
    n = int(rows[0][0])
    if n:
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} {_HIST_INSERT} {_HIST_SELECT} FROM {db}.{t} WHERE {where}",
                     params)
        delete_verified(conn, f"{db}.{t}", where, params, f"хуучин мөр ({scope})")
    return n


def clear_scope(cfg: EnvConfig, conn: Connector, scope: dict, run_id: str) -> int:
    """Тооцоолол амжилттай боловч энэ үзүүлэлтэд мөр гараагүй (жнь гарын → автомат болсон, үйл ажиллагааны SOL-д дата
    алга): өмнөх мөрийг ri_history-д хуулж устгана — хуучин утга "одоогийнх" мэт үлдэхгүй."""
    db, t = q(cfg.result_db), RESULT_TABLE
    sw, params = _scope_where(scope)
    params["r"] = run_id
    _, rows = conn.query(f"SELECT count() FROM {db}.{t} WHERE {sw}", params)
    n = int(rows[0][0])
    if n:
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} {_HIST_INSERT} {_HIST_SELECT} FROM {db}.{t} WHERE {sw}", params)
        delete_verified(conn, f"{db}.{t}", sw, params, f"мөргүй болсон үзүүлэлтийн хуучин мөр ({scope})")
    return n


def keep_only_run_many(cfg: EnvConfig, conn: Connector, pairs: list[tuple], run_id: str) -> int:
    """keep_only_run-ийн олон (risk_ind_id, snapshot_date)-ийн хувилбар (тайлант өдрийн бүх үзүүлэлт, гарын үнэлгээ:
    1,000+ мөр НЭГ удаа)."""
    if not pairs:
        return 0
    db, t = q(cfg.result_db), RESULT_TABLE
    params = {"r": run_id, "ids": sorted({str(i) for i, _ in pairs}),
              "keys": sorted({f"{i}|{d}" for i, d in pairs})}
    sw = ("risk_ind_id IN {ids:Array(String)} "
          "AND concat(risk_ind_id, '|', toString(snapshot_date)) IN {keys:Array(String)}")
    _, rows = conn.query(f"SELECT min(loaded_at) FROM {db}.{t} WHERE {sw} AND run_id = {{r:String}}", params)
    params["mine"] = rows[0][0]
    where = (f"{sw} AND run_id != {{r:String}} AND (loaded_at < {{mine:DateTime64(3)}} "
             f"OR (loaded_at = {{mine:DateTime64(3)}} AND run_id < {{r:String}}))")
    _, rows = conn.query(f"SELECT count() FROM {db}.{t} WHERE {where}", params)
    n = int(rows[0][0])
    if n:
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} {_HIST_INSERT} {_HIST_SELECT} FROM {db}.{t} WHERE {where}",
                     params)
        delete_verified(conn, f"{db}.{t}", where, params, "хуучин мөр")
    return n


def discard_run(cfg: EnvConfig, conn: Connector, scope: dict, run_id: str) -> None:
    sw, params = _scope_where(scope)
    params["r"] = run_id
    delete_verified(conn, f"{q(cfg.result_db)}.{RESULT_TABLE}", f"{sw} AND run_id = {{r:String}}", params,
                    f"энэ run-ий мөр ({scope})")


def previous_value(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date, metric: str = "value"):
    """Өмнөх тайлант өдрийн result_number. Байхгүй бол (None, None)."""
    db = q(cfg.result_db)
    _, rows = conn.query(
        f"SELECT snapshot_date, any(result_number) FROM {db}.{RESULT_TABLE} "
        f"WHERE risk_ind_id = {{i:String}} AND snapshot_date = (SELECT max(snapshot_date) FROM {db}.{RESULT_TABLE} "
        f"  WHERE risk_ind_id = {{i:String}} AND snapshot_date < {{d:Date}}) "
        f"GROUP BY snapshot_date", {"i": indicator_id, "d": report_date})
    return (rows[0][0], rows[0][1]) if rows else (None, None)


def parse_score(result) -> float | None:
    """ri_result.result → оноо (float); "Дунд" г.м. эсвэл хоосон бол None."""
    try:
        return float(result) if result not in (None, "") else None
    except (TypeError, ValueError):
        return None


def activity_inputs(cfg: EnvConfig, conn: Connector, branch_id: str, report_date) -> list[tuple]:
    """Үйл ажиллагааны (BRANCHID) нэгтгэлд: [(risk_ind_id, оноо)] — жинг catalog-оос (activities/)."""
    _, rows = conn.query(
        f"SELECT risk_ind_id, any(result) FROM {q(cfg.result_db)}.{RESULT_TABLE} "
        f"WHERE branch_id = {{b:String}} AND snapshot_date = {{d:Date}} AND risk_ind_id != '{TOTAL_ID}' "
        f"GROUP BY risk_ind_id", {"b": str(branch_id), "d": report_date})
    return [(r[0], parse_score(r[1])) for r in rows]


# ── Цэвэрлэх, харах ───────────────────────────────────────────────────────────
def _date_where(date_from, date_to, params: dict, col: str = "report_date") -> str:
    where = "1 = 1"
    if date_from:
        where += f" AND {col} >= {{d_from:Date}}"
        params["d_from"] = date_from
    if date_to:
        where += f" AND {col} <= {{d_to:Date}}"
        params["d_to"] = date_to
    return where


def count_results(cfg: EnvConfig, conn: Connector, indicator_ids: list[str], branch_ids: list[str],
                  date_from=None, date_to=None):
    params: dict = {"ids": indicator_ids or [""], "acts": [str(b) for b in branch_ids] or [""]}
    where = (f"(risk_ind_id IN {{ids:Array(String)}} OR (risk_ind_id = '{TOTAL_ID}' AND branch_id IN "
             f"{{acts:Array(String)}})) AND {_date_where(date_from, date_to, params, 'snapshot_date')}")
    _, rows = conn.query(f"SELECT snapshot_date, if(risk_ind_id = '{TOTAL_ID}', '{TOTAL_ID}', 'INDICATOR') AS k, "
                         f"count() FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE {where} GROUP BY snapshot_date, k ORDER BY snapshot_date, k", params)
    return rows, where, params


def delete_results(cfg: EnvConfig, conn: Connector, where: str, params: dict) -> None:
    delete_verified(conn, f"{q(cfg.result_db)}.{RESULT_TABLE}", where, params, "clean")


def delete_audit(cfg: EnvConfig, conn: Connector, indicator_ids: list[str], date_from=None,
                 date_to=None) -> int:
    params: dict = {"ids": indicator_ids}
    where = "indicator_id IN {ids:Array(String)} AND " + _date_where(date_from, date_to, params)
    _, rows = conn.query(f"SELECT count() FROM {q(cfg.result_db)}.{AUDIT_TABLE} WHERE {where}", params)
    if rows[0][0]:
        delete_verified(conn, f"{q(cfg.result_db)}.{AUDIT_TABLE}", where, params, "clean audit")
    return int(rows[0][0])


_SHOW = ", ".join(c for c in RESULT_COLUMNS) + ", loaded_at"


def read_rows(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date, level: str | None = None):
    """Үзүүлэлтийн тухайн өдрийн ri_result-ийн мөр (үйл ажиллагаанд НЭГ)."""
    return conn.query(f"SELECT {_SHOW} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                      f"WHERE risk_ind_id = {{i:String}} AND snapshot_date = {{d:Date}} ORDER BY branch_id",
                      {"i": indicator_id, "d": report_date})


def read_activity(cfg: EnvConfig, conn: Connector, branch_id: str, report_date):
    """Үйл ажиллагааны тухайн өдрийн бүх мөр: эхэнд TOTAL (нийт оноо), дараа нь үзүүлэлтүүд."""
    return conn.query(
        f"SELECT risk_ind_id, risk_indicator, result_number, result, solid, run_id, loaded_at "
        f"FROM {q(cfg.result_db)}.{RESULT_TABLE} WHERE branch_id = {{a:String}} AND snapshot_date = {{d:Date}} "
        f"ORDER BY risk_ind_id = '{TOTAL_ID}' DESC, risk_ind_id", {"a": str(branch_id), "d": report_date})


# ── Retry, progress ───────────────────────────────────────────────────────────
def failed_from_run(cfg: EnvConfig, conn: Connector, run_id: str) -> list[tuple]:
    _, rows = conn.query(
        f"SELECT DISTINCT indicator_id, report_date, period_start FROM {q(cfg.result_db)}.{AUDIT_TABLE} "
        f"WHERE run_id = {{r:String}} AND (execution_status IN ('FAILED', 'TIMEOUT', 'VALIDATION_FAILED') "
        f"  OR (execution_status = 'SKIPPED' AND error_code IN ('DEPENDENCY_FAILED', 'SOURCE_NOT_READY')))",
        {"r": run_id})
    return rows


def latest_status(cfg: EnvConfig, conn: Connector) -> dict:
    _, rows = conn.query(
        f"SELECT indicator_id, argMax(execution_status, started_at), argMax(report_date, started_at),"
        f"       max(started_at), argMax(error_code, started_at) "
        f"FROM {q(cfg.result_db)}.{AUDIT_TABLE} "
        f"WHERE run_mode != 'DRY_RUN' AND execution_status != 'SKIPPED' AND environment = {{env:String}} "
        f"GROUP BY indicator_id", {"env": cfg.env})
    return {r[0]: {"status": r[1], "report_date": r[2], "at": r[3], "error_code": r[4]} for r in rows}


# ── verify, auto ──────────────────────────────────────────────────────────────
VERIFY_COLUMNS = RESULT_COLUMNS


def read_indicator(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date) -> list[dict]:
    """Үзүүлэлтийн тухайн өдрийн ri_result-ийн бүх мөр (dict)."""
    cols = list(VERIFY_COLUMNS)
    _, rows = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE risk_ind_id = {{i:String}} AND snapshot_date = {{d:Date}}",
                         {"i": indicator_id, "d": report_date})
    return [dict(zip(cols, r)) for r in rows]


def read_activity_row(cfg: EnvConfig, conn: Connector, branch_id: str, report_date) -> dict | None:
    """Үйл ажиллагааны нийт онооны (TOTAL) мөр."""
    cols = list(VERIFY_COLUMNS)
    _, rows = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE branch_id = {{b:String}} AND snapshot_date = {{d:Date}} AND risk_ind_id = '{TOTAL_ID}'",
                         {"b": str(branch_id), "d": report_date})
    return dict(zip(cols, rows[0])) if len(rows) == 1 else ({"_count": len(rows)} if rows else None)


def audit_of_run(cfg: EnvConfig, conn: Connector, run_id: str, indicator_id: str, report_date):
    """(execution_status, error_code) — тухайн run-ий (үр дүнг бичсэн) audit бүртгэл."""
    _, rows = conn.query(
        f"SELECT argMax(execution_status, started_at), argMax(error_code, started_at) "
        f"FROM {q(cfg.result_db)}.{AUDIT_TABLE} WHERE run_id = {{r:String}} AND indicator_id = {{i:String}} "
        f"AND report_date = {{d:Date}}", {"r": run_id, "i": indicator_id, "d": report_date})
    return (rows[0][0], rows[0][1]) if rows and rows[0][0] else (None, None)


def written_versions(cfg: EnvConfig, conn: Connector, date_from, date_to) -> dict:
    """{(risk_ind_id, snapshot_date): sql_version} — ri_result-д одоо байгаа үзүүлэлтийн мөрүүд; хувилбар нь тэр
    мөрийг бичсэн run-ий audit-аас (ri_result-д sql_version хадгалахгүй)."""
    db = q(cfg.result_db)
    _, rows = conn.query(
        f"SELECT r.risk_ind_id AS i, r.snapshot_date AS d, a.v AS v "
        f"FROM (SELECT risk_ind_id, snapshot_date, any(run_id) AS run_id FROM {db}.{RESULT_TABLE} "
        f"      WHERE risk_ind_id != '{TOTAL_ID}' AND snapshot_date >= {{a:Date}} AND snapshot_date <= {{b:Date}} "
        f"      GROUP BY risk_ind_id, snapshot_date) AS r "
        f"LEFT JOIN (SELECT run_id, indicator_id, report_date, argMax(sql_version, started_at) AS v "
        f"           FROM {db}.{AUDIT_TABLE} WHERE report_date >= {{a:Date}} AND report_date <= {{b:Date}} "
        f"           GROUP BY run_id, indicator_id, report_date) AS a "
        f"  ON a.run_id = r.run_id AND a.indicator_id = r.risk_ind_id AND a.report_date = r.snapshot_date",
        {"a": date_from, "b": date_to})
    return {(r[0], r[1]): r[2] or None for r in rows}


def last_attempts(cfg: EnvConfig, conn: Connector, date_from, date_to) -> dict:
    """{(indicator_id, report_date): (status, sql_version)} — сүүлийн бодит оролдлого (DRY_RUN, SKIPPED-гүй)."""
    _, rows = conn.query(
        f"SELECT indicator_id, report_date, argMax(execution_status, started_at), argMax(sql_version, started_at) "
        f"FROM {q(cfg.result_db)}.{AUDIT_TABLE} WHERE run_mode != 'DRY_RUN' AND execution_status != 'SKIPPED' "
        f"AND environment = {{e:String}} AND report_date >= {{a:Date}} AND report_date <= {{b:Date}} "
        f"GROUP BY indicator_id, report_date", {"e": cfg.env, "a": date_from, "b": date_to})
    return {(r[0], r[1]): (r[2], r[3]) for r in rows}
