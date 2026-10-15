"""Oracle procedure блок (BEGIN pkg.proc(..., :rc); END;) — DB-гүй, хуурамч oracledb-ээр."""
import pytest

from ri_runner.db import OracleConnector, RunnerError


class Cursor:
    def __init__(self, rows=None, description=None, log=None):
        self.rows, self.description, self.log, self.arraysize = rows or [], description, log, 100

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def var(self, typ):
        return Var(self)

    def execute(self, sql, binds=None):
        self.log.append((sql, binds))
        if binds and "rc" in binds:
            binds["rc"].value = Cursor([("B01", 20.0)], [("BR", "VARCHAR", 0, 0, 0, None), ("PCT", "NUMBER", 0, 0, 0, -127)])

    def fetchall(self):
        return self.rows


class Var:
    def __init__(self, cur):
        self.value = None

    def getvalue(self):
        return self.value


class Conn:
    call_timeout = 0

    def __init__(self):
        self.log = []

    def cursor(self):
        return Cursor(log=self.log)

    def rollback(self):
        self.log.append(("ROLLBACK", None))

    def is_healthy(self):
        return True


def connector():
    c = object.__new__(OracleConnector)
    c.name, c.conn, c._oracledb = "oracle_test", Conn(), type("ora", (), {"DB_TYPE_CURSOR": "CURSOR"})
    return c


def test_block_returns_ref_cursor_rows():
    c = connector()
    sql = "BEGIN\n  PKG.HR(:p_date_from, :p_date_to, :p_branch_id, :rc);\nEND;"
    cols, types, rows = c.query_typed(sql, {"p_date_from": 1, "p_date_to": 2, "p_branch_id": "B01", "p_run_id": "x"})
    assert cols == ["BR", "PCT"] and rows == [("B01", 20.0)]
    _, binds = next(e for e in c.conn.log if e[0].startswith("BEGIN"))
    assert set(binds) == {"p_date_from", "p_date_to", "p_branch_id", "rc"}       # ашиглаагүй p_run_id дамжихгүй


def test_source_query_runs_in_read_only_transaction():
    """Код (procedure ч) source-д бичиж чадахгүй: READ ONLY transaction-д ажиллаад rollback."""
    c = connector()
    c.query_typed("BEGIN PKG.HR(:p_date_to, :rc); END;", {"p_date_to": 1})
    assert [e[0].split("(")[0].strip() for e in c.conn.log] == [
        "ROLLBACK", "SET TRANSACTION READ ONLY", "BEGIN PKG.HR", "ROLLBACK"]


def test_block_without_cursor_is_rejected():
    with pytest.raises(RunnerError) as e:
        connector().query_typed("BEGIN PKG.HR(:p_date_to); END;", {"p_date_to": 1})
    assert e.value.code == "PLSQL_NO_CURSOR"


def test_broken_connection_after_timeout_is_not_touched():
    """Timeout-ийн дараа тасарсан холболтод call_timeout оноовол python-oracledb процессыг унагадаг (SIGBUS)."""
    from ri_runner.db import classify_error

    class Broken(Conn):
        def cursor(self):
            cur = Cursor(log=self.log)
            def boom(sql, binds=None):
                self.log.append((sql, binds))
                if not sql.startswith("SET"):
                    raise RuntimeError("DPY-4011: the database or network closed the connection\nsocket timed out")
            cur.execute = boom
            return cur

        def is_healthy(self):
            return False

    c = connector()
    c.conn = Broken()
    with pytest.raises(RuntimeError) as e:
        c.query_typed("SELECT 1 AS X FROM dual WHERE :p_date_to IS NOT NULL", {"p_date_to": 1}, timeout=1)
    assert [x[0] for x in c.conn.log].count("ROLLBACK") == 1                 # зөвхөн эхний (эрүүл үеийн) rollback
    assert classify_error(e.value)[0] == "TIMEOUT"


def test_table_changed_is_retried(monkeypatch):
    """ORA-01466 (хүснэгт дөнгөж TRUNCATE/DDL хийгдсэн) → хүлээгээд дахин уншина."""
    monkeypatch.setattr("ri_runner.db.time.sleep", lambda s: None)
    c = connector()
    calls = {"n": 0}
    real = c._query_once

    def flaky(sql, params, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("ORA-01466: unable to read data - table definition has changed")
        return real(sql, params, timeout)
    c._query_once = flaky
    cols, _, rows = c.query_typed("BEGIN PKG.HR(:p_date_to, :rc); END;", {"p_date_to": 1})
    assert calls["n"] == 2 and rows == [("B01", 20.0)]
    c._query_once = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ORA-00942: table or view does not exist"))
    with pytest.raises(RuntimeError):
        c.query_typed("SELECT 1 FROM dual", {})                                # бусад алдааг давтахгүй
