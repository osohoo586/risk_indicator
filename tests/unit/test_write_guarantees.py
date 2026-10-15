"""Source зөвхөн уншина, ClickHouse-д бичсэнийг буцааж тулгана, auto зөвхөн дутуу/хуучирсныг (DB-гүй)."""
import datetime as dt

import pytest

from ri_runner import auto, checks, store
from ri_runner.db import RunnerError, classify_error
from ri_runner.verify import compare

D = dt.date(2026, 9, 30)


def test_dialect_must_match_connection():
    ch_in_oracle = checks.dialect_errors("RI", "SELECT 1 FROM t WHERE d = {p_date_to:Date}", "oracle", "oracle_whouse")
    ora_in_ch = checks.dialect_errors("RI", "SELECT 1 FROM t WHERE d = :p_date_to", "clickhouse", "clickhouse_dwh")
    assert "ClickHouse параметр ({p_date_to:...}) Oracle connection" in ch_in_oracle[0]
    assert "Oracle параметр (:p_date_to) ClickHouse connection" in ora_in_ch[0]
    assert not checks.dialect_errors("RI", "SELECT x::Date FROM t WHERE d = {p_date_to:Date}", "clickhouse", "c")
    assert not checks.dialect_errors("RI", "SELECT 1 FROM {{schema.erp}}.T WHERE d = :p_date_to", "oracle", "o")


def test_code_may_not_modify_source():
    for code in ("BEGIN EXECUTE IMMEDIATE 'x'; END;", "SELECT a FROM t FOR UPDATE",
                 "OPTIMIZE TABLE t FINAL", "SYSTEM FLUSH LOGS", "SELECT a FROM t INTO OUTFILE 'f'"):
        errors, _ = checks._rule_errors("RI", code)
        assert errors, code
    assert not checks._rule_errors("RI", "SELECT a.SYSTEM_ID AS X, a.UPDATED_AT AS Y FROM t a")[0]


def test_timeouts_are_classified():
    for msg in ("DPY-4011: the database or network closed the connection\nsocket timed out while recovering",
                "Code: 159. DB::Exception: Timeout exceeded: elapsed 1000 ms",
                "Code: 160. DB::Exception: Estimated query execution time (12 seconds) is too long. (TOO_SLOW)"):
        assert classify_error(Exception(msg))[0] == "TIMEOUT", msg


def test_source_write_is_classified():
    code, msg = classify_error(Exception("ORA-01456: may not perform insert ... READ ONLY transaction"))
    assert code == "SOURCE_WRITE_BLOCKED" and "зөвхөн уншина" in msg


def _row(**kw):
    base = {"row_type": "INDICATOR", "report_date": D, "indicator_id": "RI_05_0001", "branch_id": "998",
            "entity_level": "ACTIVITY", "entity_id": "998", "metric": "value", "activity_id": "ACT_05",
            "sol_id": "808,810", "file_name": "activities/act_05_test/ri_05_0001.sql", "value": 0.95,
            "numerator": 95.0, "denominator": 100.0, "score": 3.0, "weight": 1.5}
    base.update(kw)
    return base


def test_written_diff():
    sent = [_row(), _row(entity_level="SOL", entity_id="808", sol_id="808", score=None, weight=None)]
    assert store.written_diff(sent, [dict(r) for r in sent]) == []
    assert "SOL 808 value: ClickHouse-д алга" in store.written_diff(sent, [dict(sent[0])])
    assert "value 0.95 ≠ 0.94" in store.written_diff(sent, [_row(value=0.94), dict(sent[1])])[0]
    assert "sol_id '808,810' ≠ '808'" in store.written_diff(sent, [_row(sol_id="808"), dict(sent[1])])[0]
    assert "2 удаа бичигдсэн" in store.written_diff(sent[:1], [_row(), _row()])[0]
    assert store.written_diff(sent[:1], [_row(), dict(sent[1])]) == ["SOL 808 value: илүү мөр (1)"]


class FakeCH:
    """insert → SELECT (буцааж унших) → DELETE (зөрвөл) дарааллыг бичнэ. tamper: ClickHouse-д өөр утга хадгалагдсан мэт."""
    def __init__(self, tamper=None, sticky_deletes=0):
        self.rows, self.calls, self.tamper, self.sticky_deletes = [], [], tamper, sticky_deletes

    def insert(self, db, table, cols, data):
        self.calls.append("INSERT")
        self.rows = [dict(zip(cols, r)) for r in data]
        if self.tamper:
            self.rows[0].update(self.tamper)

    def query(self, sql, params=None):
        self.calls.append("SELECT")
        if "count()" in sql:
            return ["c"], [[len(self.rows)]]
        cols = [c.strip() for c in sql.split("SELECT", 1)[1].split("FROM", 1)[0].split(",")]
        return cols, [[r.get(c) for c in cols] for r in self.rows]

    def execute(self, sql, params=None):
        self.calls.append(sql.split()[0])
        if sql.startswith("DELETE") and self.sticky_deletes:
            self.sticky_deletes -= 1                       # ClickHouse-д DELETE-ийн дараа мөр үлдсэн мэт
        elif sql.startswith("DELETE"):
            self.rows = []


class Cfg:
    result_db = "risk_assessment_test"
    result_connection = "clickhouse_ra"


def test_insert_is_read_back_and_rolled_back_on_mismatch():
    scope = {"indicator_id": "RI_05_0001", "report_date": D, "row_type": "INDICATOR"}
    ok = FakeCH()
    store.insert_result_verified(Cfg, ok, [_row()], scope, "run1")
    assert ok.calls == ["INSERT", "SELECT"]
    bad = FakeCH(tamper={"value": 0.5})
    with pytest.raises(RunnerError) as exc:
        store.insert_result_verified(Cfg, bad, [_row()], scope, "run1")
    assert exc.value.code == "INSERT_MISMATCH" and "value 0.95 ≠ 0.5" in str(exc.value)
    assert bad.calls == ["INSERT", "SELECT", "DELETE", "SELECT"]   # бичсэнээ устгаж (шалгаж) хуучин нь үлдэнэ


def test_delete_is_verified_and_retried(monkeypatch):
    """DELETE-ийн дараа мөр үлдвэл дахин; DELETE_RETRIES удаа үлдвэл DELETE_INCOMPLETE (чимээгүй давхардахгүй)."""
    monkeypatch.setattr(store.time, "sleep", lambda s: None)
    once = FakeCH(sticky_deletes=1)
    once.rows = [_row()]
    store.delete_verified(once, "db.t", "1 = 1", {}, "тест")
    assert once.calls == ["DELETE", "SELECT", "DELETE", "SELECT"] and once.rows == []
    stuck = FakeCH(sticky_deletes=99)
    stuck.rows = [_row()]
    with pytest.raises(RunnerError) as exc:
        store.delete_verified(stuck, "db.t", "1 = 1", {}, "тест")
    assert exc.value.code == "DELETE_INCOMPLETE" and stuck.calls.count("DELETE") == store.DELETE_RETRIES


def test_verify_compare():
    exp = [_row(), _row(entity_level="SOL", entity_id="808", sol_id="808")]
    assert compare(exp, [dict(r) for r in exp]) == []
    diff = compare(exp, [_row(score=4.0), dict(exp[1])])
    assert "score: тооцоо=3.0 ClickHouse=4.0" in diff[0]
    assert compare(exp, [dict(exp[0])]) == ["SOL 808 value: ClickHouse-д алга"]


def test_due_dates(make_ind):
    q = make_ind(frequency="quarterly")
    m = make_ind(frequency="monthly")
    assert auto.due_dates(q, dt.date(2026, 1, 1), dt.date(2026, 10, 13)) == [
        dt.date(2026, 3, 31), dt.date(2026, 6, 30), D]
    assert auto.due_dates(m, dt.date(2026, 8, 1), dt.date(2026, 10, 13)) == [dt.date(2026, 8, 31), D]


def test_auto_plan_reasons(make_ind, monkeypatch):
    a = make_ind(indicator_id="RI_05_0001")                                   # бэлэн
    b = make_ind(indicator_id="RI_05_0002")                                   # код өөрчлөгдсөн
    c = make_ind(indicator_id="RI_05_0003", dependencies=["RI_05_0002"])      # бэлэн, гэхдээ 0002-оос хамаарна
    d = make_ind(indicator_id="RI_05_0004")                                   # сүүлийн оролдлого алдаатай
    e = make_ind(indicator_id="RI_05_0005")                                   # огт ажиллаагүй
    f = make_ind(indicator_id="RI_05_0006")                                   # source 0 мөр (WARNING) — бэлэн
    cat = type("Cat", (), {"calcs": {}})()
    ctx = type("Ctx", (), {"cfg": Cfg, "cat": cat})()
    v = {i.indicator_id: auto.version_of(cat, i) for i in (a, b, c, d, e, f)}
    monkeypatch.setattr(auto.store, "ensure_base", lambda *a, **k: False)
    monkeypatch.setattr(auto.store, "written_versions", lambda *a: {
        ("RI_05_0001", D): v["RI_05_0001"], ("RI_05_0002", D): "0.0.1+old", ("RI_05_0003", D): v["RI_05_0003"],
        ("RI_05_0004", D): v["RI_05_0004"]})
    monkeypatch.setattr(auto.store, "last_attempts", lambda *a: {
        ("RI_05_0001", D): ("SUCCESS", v["RI_05_0001"]), ("RI_05_0004", D): ("VALIDATION_FAILED", v["RI_05_0004"]),
        ("RI_05_0006", D): ("WARNING", v["RI_05_0006"])})

    class Conn:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    monkeypatch.setattr(auto, "connect", lambda *a, **k: Conn())
    plan, items = auto.build_plan(ctx, [a, b, c, d, e, f], dt.date(2026, 9, 1), dt.date(2026, 10, 13))
    reasons = {i.indicator_id: r for i, _, r, _ in items}
    assert reasons == {"RI_05_0002": "ӨӨРЧЛӨГДСӨН", "RI_05_0003": "ХАМААРАЛ", "RI_05_0004": "АЛДАА",
                       "RI_05_0005": "ШИНЭ"}
    assert sorted(i.indicator_id for i in plan[D]) == sorted(reasons)
