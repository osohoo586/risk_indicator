"""ClickHouse: НЭГ үр дүнгийн хүснэгт (riskassessment.ri_result) + audit + history.

Бичих нэгж (scope):
  INDICATOR мөрүүд — (indicator_id, report_date, row_type='INDICATOR')
  ACTIVITY мөрүүд  — (branch_id, report_date, row_type='ACTIVITY')   (1 BRANCHID = 1 үйл ажиллагаа)

Бичих: шинэ мөрийг run_id-тай бичээд ClickHouse-оос БУЦААЖ уншиж мөр бүрийг тулгана (insert_result_verified) —
зөрвөл энэ run-ий мөрийг устгаад алдаа (FAILED, хуучин утга хэвээр). Мөр бүрт ACTIVITY (activity_id, branch_id),
SOLID (sol_id), файл (file_name) metadata.
Дахин ажиллуулах: шинэ мөрийг run_id-тай бичээд, шалгалт давбал тухайн scope-ийн хуучин мөрүүдийг
ri_history-д (JSON) хуулж устгана. Зэрэг ажилласан run-уудаас хамгийн сүүлд бичсэн нь үлдэнэ.
Шалгалт унавал (prod) шинэ мөрийг устгаж хуучин нь үлдэнэ.
"""
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
VIEWS = ("v_activity_score", "v_indicator_score", "v_indicator_detail", "v_risk_indicators")
AUDIT_TABLE = "ri_execution_audit"
HISTORY_TABLE = "ri_history"

RESULT_COLUMNS = ("report_date", "period_start", "row_type", "group_no", "activity_id", "branch_id", "sol_id",
                  "activity_name", "indicator_id", "indicator_name", "calc_id", "source_kind", "file_name",
                  "entity_level", "entity_id", "entity_name", "parent_id", "metric", "numerator",
                  "denominator", "value", "value_text", "score", "score_label", "weight", "level",
                  "n_indicators", "n_scored", "weight_coverage", "data_status", "score_type",
                  "scale_version", "source_row_count", "comment", "entered_by", "run_id", "sql_version")
AUDIT_COLUMNS = ("run_id", "run_mode", "activity_id", "indicator_id", "report_date", "period_start",
                 "execution_status", "started_at", "finished_at", "duration_seconds",
                 "affected_rows", "source_row_count", "result_row_count", "validation_detail",
                 "error_code", "error_message", "executed_by", "environment", "sql_version",
                 "connection_name", "target_table")

# SQL-ийн стандарт багана
STD_REQUIRED = ("ENTITY_LEVEL", "ENTITY_ID", "VALUE")
STD_OPTIONAL = ("ENTITY_NAME", "METRIC", "NUMERATOR", "DENOMINATOR", "VALUE_TEXT", "SOURCE_ROW_COUNT",
                "DATA_STATUS")
# Өмнө нь үүссэн ri_result-д шинээр нэмэгдсэн баганууд (ALTER ... IF NOT EXISTS)
RESULT_NEW_COLUMNS = (("sol_id", "String DEFAULT '' AFTER branch_id"), ("file_name", "String DEFAULT '' AFTER source_kind"))


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
    for table, file in ((RESULT_TABLE, "ri_result.sql"), (HISTORY_TABLE, "ri_history.sql"),
                        (AUDIT_TABLE, "ri_execution_audit.sql"), (ACTIVITY_TABLE, "ri_activity.sql"),
                        (INDICATOR_TABLE, "ri_indicator.sql")):
        if not conn.table_exists(cfg.result_db, table):
            _run_ddl(cfg, conn, file)
            log(f"Хүснэгт үүсгэлээ: {cfg.result_db}.{table}")
            created = True
    have = set(conn.table_columns(cfg.result_db, RESULT_TABLE))
    for col, typ in RESULT_NEW_COLUMNS:
        if col not in have:
            conn.execute(f"ALTER TABLE {q(cfg.result_db)}.{RESULT_TABLE} ADD COLUMN IF NOT EXISTS {col} {typ}")
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
# Nullable биш баганууд: утга өгөөгүй бол
NOT_NULL_DEFAULTS = {"row_type": "", "group_no": 0, "activity_id": "", "branch_id": "", "sol_id": "",
                     "file_name": "", "activity_name": "",
                     "indicator_id": "", "indicator_name": "", "calc_id": "", "source_kind": "",
                     "entity_level": "", "entity_id": "", "metric": "value", "level": "", "data_status": "OK",
                     "score_type": "", "scale_version": "", "run_id": "", "sql_version": ""}


def insert_result(cfg: EnvConfig, conn: Connector, rows: list[dict]) -> None:
    if rows:
        data = [[NOT_NULL_DEFAULTS[c] if r.get(c) is None and c in NOT_NULL_DEFAULTS else r.get(c)
                 for c in RESULT_COLUMNS] for r in rows]
        conn.insert(cfg.result_db, RESULT_TABLE, list(RESULT_COLUMNS), data)


# Буцааж уншиж тулгах түлхүүр, утгын баганууд
_KEY = ("row_type", "report_date", "indicator_id", "branch_id", "entity_level", "entity_id", "metric")
_CHECK = ("activity_id", "sol_id", "file_name", "numerator", "denominator", "value", "value_text", "score", "weight",
          "level", "data_status", "report_date")


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
        k = f"{r.get('entity_level')} {r.get('entity_id')} {r.get('metric')}"
        if not rows:
            problems.append(f"{k}: ClickHouse-д алга")
            continue
        if len(rows) > 1:
            problems.append(f"{k}: {len(rows)} удаа бичигдсэн")
        diff = [f"{c} {r.get(c)!r} ≠ {rows[0].get(c)!r}" for c in _CHECK if c in r and not _same(r.get(c), rows[0].get(c))]
        if diff:
            problems.append(f"{k}: " + ", ".join(diff[:3]))
    problems += [f"{k[4]} {k[5]} {k[6]}: илүү мөр ({len(v)})" for k, v in have.items()]
    return problems


def insert_result_verified(cfg: EnvConfig, conn: Connector, rows: list[dict], scope: dict, run_id: str) -> None:
    """Бичээд ClickHouse-оос буцааж уншиж мөр бүрийг тулгана. Зөрвөл энэ run-ий мөрийг устгаад RunnerError
    (INSERT_MISMATCH) — бүгд зөв бичигдсэн, эсвэл юу ч үлдэхгүй (хуучин утга хэвээр)."""
    insert_result(cfg, conn, rows)
    sw, params = _scope_where(scope)
    params["r"] = run_id
    cols = list(dict.fromkeys(_KEY + _CHECK))
    _, got = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                        f"WHERE {sw} AND run_id = {{r:String}}", params)
    sent = [{c: (r.get(c) if r.get(c) is not None else NOT_NULL_DEFAULTS.get(c)) for c in cols} for r in rows]
    problems = written_diff(sent, [dict(zip(cols, g)) for g in got])
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
        parts.append(f"{k} = {{s_{k}:{'Date' if k == 'report_date' else 'String'}}}")
        params[f"s_{k}"] = v
    return " AND ".join(parts), params


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
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} "
                     f"(indicator_id, table_name, report_date, run_id, replaced_by_run, row_json) "
                     f"SELECT if(row_type = 'ACTIVITY', concat('BR_', branch_id), indicator_id), '{t}', report_date, run_id, "
                     f"{{r:String}}, formatRowNoNewline('JSONEachRow', *) FROM {db}.{t} WHERE {where}", params)
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
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} "
                     f"(indicator_id, table_name, report_date, run_id, replaced_by_run, row_json) "
                     f"SELECT indicator_id, '{t}', report_date, run_id, {{r:String}}, "
                     f"formatRowNoNewline('JSONEachRow', *) FROM {db}.{t} WHERE {sw}", params)
        delete_verified(conn, f"{db}.{t}", sw, params, f"мөргүй болсон үзүүлэлтийн хуучин мөр ({scope})")
    return n


def keep_only_run_many(cfg: EnvConfig, conn: Connector, pairs: list[tuple], run_id: str) -> int:
    """keep_only_run-ийн олон (indicator_id, report_date)-ийн хувилбар (гарын үнэлгээ: 1,000+ мөр НЭГ удаа)."""
    if not pairs:
        return 0
    db, t = q(cfg.result_db), RESULT_TABLE
    params = {"r": run_id, "ids": sorted({str(i) for i, _ in pairs}),
              "keys": sorted({f"{i}|{d}" for i, d in pairs})}
    sw = ("row_type = 'INDICATOR' AND indicator_id IN {ids:Array(String)} "
          "AND concat(indicator_id, '|', toString(report_date)) IN {keys:Array(String)}")
    _, rows = conn.query(f"SELECT min(loaded_at) FROM {db}.{t} WHERE {sw} AND run_id = {{r:String}}", params)
    params["mine"] = rows[0][0]
    where = (f"{sw} AND run_id != {{r:String}} AND (loaded_at < {{mine:DateTime64(3)}} "
             f"OR (loaded_at = {{mine:DateTime64(3)}} AND run_id < {{r:String}}))")
    _, rows = conn.query(f"SELECT count() FROM {db}.{t} WHERE {where}", params)
    n = int(rows[0][0])
    if n:
        conn.execute(f"INSERT INTO {db}.{HISTORY_TABLE} "
                     f"(indicator_id, table_name, report_date, run_id, replaced_by_run, row_json) "
                     f"SELECT indicator_id, '{t}', report_date, run_id, {{r:String}}, "
                     f"formatRowNoNewline('JSONEachRow', *) FROM {db}.{t} WHERE {where}", params)
        delete_verified(conn, f"{db}.{t}", where, params, "гарын үнэлгээний хуучин мөр")
    return n


def discard_run(cfg: EnvConfig, conn: Connector, scope: dict, run_id: str) -> None:
    sw, params = _scope_where(scope)
    params["r"] = run_id
    delete_verified(conn, f"{q(cfg.result_db)}.{RESULT_TABLE}", f"{sw} AND run_id = {{r:String}}", params,
                    f"энэ run-ий мөр ({scope})")


def previous_value(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date, metric: str = "value"):
    """Өмнөх report_date-ийн үйл ажиллагааны түвшний утга. Байхгүй бол (None, None)."""
    db = q(cfg.result_db)
    _, rows = conn.query(
        f"SELECT report_date, any(value) FROM {db}.{RESULT_TABLE} "
        f"WHERE indicator_id = {{i:String}} AND row_type = 'INDICATOR' AND entity_level = 'ACTIVITY' "
        f"AND metric = {{m:String}} AND report_date = (SELECT max(report_date) FROM {db}.{RESULT_TABLE} "
        f"  WHERE indicator_id = {{i:String}} AND row_type = 'INDICATOR' AND report_date < {{d:Date}}) "
        f"GROUP BY report_date", {"i": indicator_id, "d": report_date, "m": metric})
    return (rows[0][0], rows[0][1]) if rows else (None, None)


def activity_inputs(cfg: EnvConfig, conn: Connector, branch_id: str, report_date) -> list[tuple]:
    """Үйл ажиллагааны (BRANCHID) нэгтгэлд: (indicator_id, score, weight) — ACTIVITY түвшний мөрүүд."""
    _, rows = conn.query(
        f"SELECT indicator_id, any(score), any(weight) FROM {q(cfg.result_db)}.{RESULT_TABLE} "
        f"WHERE branch_id = {{b:String}} AND report_date = {{d:Date}} AND row_type = 'INDICATOR' "
        f"AND entity_level = 'ACTIVITY' GROUP BY indicator_id", {"b": str(branch_id), "d": report_date})
    return rows


# ── Цэвэрлэх, харах ───────────────────────────────────────────────────────────
def _date_where(date_from, date_to, params: dict) -> str:
    where = "1 = 1"
    if date_from:
        where += " AND report_date >= {d_from:Date}"
        params["d_from"] = date_from
    if date_to:
        where += " AND report_date <= {d_to:Date}"
        params["d_to"] = date_to
    return where


def count_results(cfg: EnvConfig, conn: Connector, indicator_ids: list[str], branch_ids: list[str],
                  date_from=None, date_to=None):
    params: dict = {"ids": indicator_ids or [""], "acts": [str(b) for b in branch_ids] or [""]}
    where = (f"(indicator_id IN {{ids:Array(String)}} OR (row_type = 'ACTIVITY' AND branch_id IN "
             f"{{acts:Array(String)}})) AND {_date_where(date_from, date_to, params)}")
    _, rows = conn.query(f"SELECT report_date, row_type, count() FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE {where} GROUP BY report_date, row_type ORDER BY report_date, row_type", params)
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


def read_rows(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date, level: str | None = None):
    params = {"i": indicator_id, "d": report_date}
    lvl = ""
    if level:
        lvl = " AND entity_level = {l:String}"
        params["l"] = level.upper()
    return conn.query(
        f"SELECT entity_level, entity_id, entity_name, metric, numerator, denominator, value, value_text, "
        f"score, score_label, weight, data_status, run_id, sql_version FROM {q(cfg.result_db)}.{RESULT_TABLE} "
        f"WHERE indicator_id = {{i:String}} AND report_date = {{d:Date}} AND row_type = 'INDICATOR'{lvl} "
        f"ORDER BY entity_level = 'ACTIVITY' DESC, entity_level, entity_id, metric", params)


def read_activity(cfg: EnvConfig, conn: Connector, branch_id: str, report_date):
    return conn.query(
        f"SELECT row_type, indicator_id, indicator_name, source_kind, value, value_text, score, score_label, "
        f"weight, level, n_indicators, n_scored, weight_coverage, data_status "
        f"FROM {q(cfg.result_db)}.{RESULT_TABLE} WHERE branch_id = {{a:String}} AND report_date = {{d:Date}} "
        f"AND (row_type = 'ACTIVITY' OR entity_level = 'ACTIVITY') "
        f"ORDER BY row_type = 'ACTIVITY' DESC, indicator_id", {"a": str(branch_id), "d": report_date})


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
VERIFY_COLUMNS = ("row_type", "indicator_id", "activity_id", "branch_id", "sol_id", "file_name", "entity_level",
                  "entity_id", "metric", "numerator", "denominator", "value", "value_text", "score", "weight",
                  "level", "n_scored", "period_start", "run_id", "sql_version")


def read_indicator(cfg: EnvConfig, conn: Connector, indicator_id: str, report_date) -> list[dict]:
    """Үзүүлэлтийн тухайн өдрийн ri_result-ийн бүх мөр (dict)."""
    cols = list(VERIFY_COLUMNS)
    _, rows = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE indicator_id = {{i:String}} AND report_date = {{d:Date}} AND row_type = 'INDICATOR'",
                         {"i": indicator_id, "d": report_date})
    return [dict(zip(cols, r)) for r in rows]


def read_activity_row(cfg: EnvConfig, conn: Connector, branch_id: str, report_date) -> dict | None:
    cols = list(VERIFY_COLUMNS)
    _, rows = conn.query(f"SELECT {', '.join(cols)} FROM {q(cfg.result_db)}.{RESULT_TABLE} "
                         f"WHERE branch_id = {{b:String}} AND report_date = {{d:Date}} AND row_type = 'ACTIVITY'",
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
    """{(indicator_id, report_date): sql_version} — ri_result-д одоо байгаа үзүүлэлтийн мөрүүд."""
    _, rows = conn.query(
        f"SELECT indicator_id, report_date, any(sql_version) FROM {q(cfg.result_db)}.{RESULT_TABLE} "
        f"WHERE row_type = 'INDICATOR' AND entity_level = 'ACTIVITY' "
        f"AND report_date >= {{a:Date}} AND report_date <= {{b:Date}} GROUP BY indicator_id, report_date",
        {"a": date_from, "b": date_to})
    return {(r[0], r[1]): r[2] for r in rows}


def last_attempts(cfg: EnvConfig, conn: Connector, date_from, date_to) -> dict:
    """{(indicator_id, report_date): (status, sql_version)} — сүүлийн бодит оролдлого (DRY_RUN, SKIPPED-гүй)."""
    _, rows = conn.query(
        f"SELECT indicator_id, report_date, argMax(execution_status, started_at), argMax(sql_version, started_at) "
        f"FROM {q(cfg.result_db)}.{AUDIT_TABLE} WHERE run_mode != 'DRY_RUN' AND execution_status != 'SKIPPED' "
        f"AND environment = {{e:String}} AND report_date >= {{a:Date}} AND report_date <= {{b:Date}} "
        f"GROUP BY indicator_id, report_date", {"e": cfg.env, "a": date_from, "b": date_to})
    return {(r[0], r[1]): (r[2], r[3]) for r in rows}
