"""DB connection-ууд.

Source: Oracle (python-oracledb, thin mode) эсвэл ClickHouse (clickhouse-connect) — ЗӨВХӨН УНШИНА:
  Oracle      query бүр READ ONLY transaction-д (INSERT/UPDATE/DELETE → ORA-01456), дараа нь rollback
  ClickHouse  connect(..., read_only=True) → query бүрт readonly=2 (бичих, DDL → Code: 164)
Үр дүн: ClickHouse (risk_assessment.ri_result + audit, history) — зөвхөн result connection бичнэ.
"""
import datetime as dt
import decimal
import os
import re
import threading
import time

from .config import ConfigError, EnvConfig
from .sqltext import is_plsql_block, oracle_binds_used

# DPY-4011 "socket timed out": call_timeout-ийн дараа холболт тасарсан (thin driver break-ийг хүлээж чадаагүй)
# ClickHouse TOO_SLOW "Estimated query execution time": timeout_seconds-оос удаан болно гэж урьдчилан тооцоод зогсоосон
_TIMEOUT_MARKERS = ("DPY-4024", "ORA-03156", "ORA-01013", "socket timed out", "TIMEOUT_EXCEEDED", "Code: 159",
                    "Estimated query execution time")
_ERROR_CODE_RE = re.compile(r"\b(ORA-\d{5}|DPY-\d{4}|DPI-\d{4}|Code: \d+)")
_READ_ONLY_MARKERS = ("ORA-01456", "Code: 164", "attempt to write a readonly database")


class RunnerError(Exception):
    """Runner-ийн өөрийн алдаа (code-той)."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


# ── Төрөл: source-ийн баганын төрөл (dry-run-д харуулна) ──────────────────────
def base_type(ch_type: str) -> str:
    """Nullable(...)/LowCardinality(...)-ийг хасна."""
    while True:
        m = re.match(r"^(Nullable|LowCardinality)\((.*)\)$", ch_type)
        if not m:
            return ch_type
        ch_type = m.group(2)


def nullable(ch_type: str) -> str:
    if base_type(ch_type) == "Nothing":                  # бүх утга NULL (SELECT NULL AS X)
        return "Nullable(String)"
    if ch_type.startswith(("Nullable(", "LowCardinality(", "Array(", "Map(", "Tuple(")):
        return ch_type
    return f"Nullable({ch_type})"


def type_family(ch_type: str) -> str:
    """Төрлийн бүлэг: number / date / string / other. Бүлэг өөрчлөгдвөл хүснэгтэд бичих боломжгүй."""
    t = base_type(ch_type)
    if t.startswith(("Int", "UInt", "Float", "Decimal", "Bool")):
        return "number"
    if t.startswith(("Date", "DateTime")):
        return "date"
    if t.startswith(("String", "FixedString", "UUID", "Enum")):
        return "string"
    return "other"


def oracle_to_ch_type(type_code, precision, scale) -> str:
    name = getattr(type_code, "name", str(type_code)).upper()
    if "NUMBER" in name:
        p, s = precision or 0, scale if scale is not None else -127
        if s == 0 and 0 < p <= 18:
            return "Nullable(Int64)"
        if s == 0 and 18 < p <= 38:                      # урт ID/данс: Float болгвол орон гэмтэнэ
            return f"Nullable(Decimal({p}, 0))"
        if 0 < p <= 38 and 0 < s <= p:
            return f"Nullable(Decimal({p}, {s}))"
        return "Nullable(Float64)"
    if any(k in name for k in ("BINARY_DOUBLE", "BINARY_FLOAT")):
        return "Nullable(Float64)"
    if any(k in name for k in ("BINARY_INTEGER", "BOOLEAN")):
        return "Nullable(Int64)"
    if name.endswith("DB_TYPE_DATE"):
        return "Nullable(DateTime64(0))"         # Oracle DATE цагтай; DateTime64: 1900–2299 (DateTime нь 1970-аас)
    if "TIMESTAMP" in name:
        return "Nullable(DateTime64(6))"
    return "Nullable(String)"


def convert_value(value, ch_type: str):
    """Python утгыг ClickHouse-ийн баганын төрөлд тааруулна."""
    if value is None:
        return None
    t = base_type(ch_type)
    if isinstance(value, float) and value != value:          # NaN
        return None
    if t.startswith(("Int", "UInt")):
        return int(value)
    if t.startswith("Float"):
        return float(value)
    if t.startswith("Decimal"):
        return value if isinstance(value, decimal.Decimal) else decimal.Decimal(str(value))
    if t.startswith("DateTime"):
        if isinstance(value, dt.datetime):
            return value.replace(tzinfo=None)
        if isinstance(value, dt.date):
            return dt.datetime.combine(value, dt.time())
        return value
    if t in ("Date", "Date32"):
        return value.date() if isinstance(value, dt.datetime) else value
    if t == "String" and not isinstance(value, str):
        return str(value)
    return value


# ── Connector-ууд ─────────────────────────────────────────────────────────────
class Connector:
    type = "base"
    read_only = False

    def query(self, sql: str, params: dict, timeout: int | None = None):
        """(column_names, rows) буцаана."""
        cols, _, rows = self.query_typed(sql, params, timeout)
        return cols, rows

    def query_typed(self, sql: str, params: dict, timeout: int | None = None):
        """(column_names, clickhouse_types, rows) буцаана."""
        raise NotImplementedError

    def execute(self, sql: str, params=None) -> None:
        raise NotImplementedError

    def insert(self, database: str, table: str, columns: list[str], rows: list) -> None:
        raise NotImplementedError

    def table_columns(self, database: str, table: str) -> list[str]:
        """Хүснэгтийн баганууд (жижиг үсгээр). Хүснэгт байхгүй бол хоосон."""
        raise NotImplementedError

    def table_exists(self, database: str, table: str) -> bool:
        return bool(self.table_columns(database, table))

    def table_column_types(self, database: str, table: str) -> dict[str, str]:
        """{багана: төрөл}. Хүснэгт байхгүй бол хоосон."""
        raise NotImplementedError

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


_THICK_DONE = False
_THICK_LOCK = threading.Lock()


def _init_oracle_client(oracledb) -> None:
    """Хуучин Oracle (thin горимд холбогдохгүй) бол Instant Client (thick) ашиглана.

    .env:  ORACLE_CLIENT_LIB=C:\\Users\\...\\instantclient_21_13
           ORACLE_CLIENT_CONFIG=C:\\Users\\...\\instantclient_21_13\\network\\admin   (tnsnames.ora, заавал биш)
    Хоосон бол thin горим (Instant Client хэрэггүй).
    """
    global _THICK_DONE
    lib = os.environ.get("ORACLE_CLIENT_LIB", "").strip()
    if _THICK_DONE or not lib:
        return
    with _THICK_LOCK:                                # зэрэг ажиллах thread-ууд нэг л удаа ачаална
        if _THICK_DONE:
            return
        kw = {"lib_dir": lib}
        if os.environ.get("ORACLE_CLIENT_CONFIG", "").strip():
            kw["config_dir"] = os.environ["ORACLE_CLIENT_CONFIG"].strip()
        try:
            oracledb.init_oracle_client(**kw)
        except Exception as exc:  # noqa: BLE001
            raise ConfigError(f"Oracle Instant Client ачаалж чадсангүй (ORACLE_CLIENT_LIB={lib}): {exc}") from exc
        _THICK_DONE = True


class OracleConnector(Connector):
    """Зөвхөн source: query бүр READ ONLY transaction-д. Параметрийг SQL-д :p_report_date хэлбэрээр бичнэ."""
    type = "oracle"
    read_only = True

    def __init__(self, name: str, cfg: dict, read_only: bool = True):
        try:
            import oracledb
        except ImportError as exc:
            raise ConfigError("oracledb суугаагүй байна: pip install -r requirements.txt") from exc
        _init_oracle_client(oracledb)
        oracledb.defaults.fetch_lobs = False          # CLOB-ийг string-ээр авна
        oracledb.defaults.fetch_decimals = True       # NUMBER → Decimal (float-оор мөнгөн дүнгийн орон гэмтэхгүй)
        if cfg.get("connect_string"):
            # user/password@host:port/service хэлбэр (хуучин connStr-тэй ижил)
            cs = cfg["connect_string"]
            if "/" not in cs.split("@")[0] or "@" not in cs:
                raise ConfigError(f"{name}: connect_string нь user/password@dsn хэлбэртэй байх ёстой")
            creds, dsn = cs.rsplit("@", 1)
            user, password = creds.split("/", 1)
        else:
            user, password, dsn = cfg.get("user"), cfg.get("password"), cfg.get("dsn")
        if not (user and password and dsn):
            raise ConfigError(f"{name}: user/password/dsn эсвэл connect_string дутуу")
        self.name = name
        self._oracledb = oracledb
        self.conn = oracledb.connect(user=user, password=password, dsn=dsn)

    RETRY_CHANGED = (2, 2.0)       # ORA-01466: (дахин оролдох тоо, хүлээх сек)

    def query_typed(self, sql, params, timeout=None):
        """SELECT эсвэл procedure дуудах блок (BEGIN pkg.proc(..., :rc); END;) — блокийн үр дүнг :rc cursor-оос.

        ORA-01466: хүснэгт дөнгөж өөрчлөгдсөн (DDL, TRUNCATE — ETL ачаалж байна) үед READ ONLY transaction ~1 сек уншиж
        чаддаггүй. Зөвхөн уншдаг тул хүлээгээд дахин оролдоно.
        """
        tries, wait = self.RETRY_CHANGED
        for attempt in range(tries + 1):
            try:
                return self._query_once(sql, params, timeout)
            except Exception as exc:  # noqa: BLE001
                if "ORA-01466" not in str(exc) or attempt == tries:
                    raise
                time.sleep(wait)

    def _query_once(self, sql, params, timeout=None):
        used = oracle_binds_used(sql)
        binds = {k: v for k, v in params.items() if k.lower() in used and k.lower() != "rc"}
        self.conn.call_timeout = int(timeout * 1000) if timeout else 0
        try:
            with self.conn.cursor() as cur:
                cur.arraysize = 5000
                # Source-д юу ч бичихгүй: procedure дотор ч INSERT/UPDATE/DELETE → ORA-01456.
                # SET TRANSACTION нь transaction-ий эхний statement байх ёстой тул өмнөхийг дуусгана.
                self.conn.rollback()
                cur.execute("SET TRANSACTION READ ONLY")
                if is_plsql_block(sql):
                    if "rc" not in used:
                        raise RunnerError("PLSQL_NO_CURSOR", "Procedure блок үр дүнгээ :rc (SYS_REFCURSOR)-оор "
                                                             "буцаах ёстой: BEGIN pkg.proc(..., :rc); END;")
                    rc = cur.var(self._oracledb.DB_TYPE_CURSOR)
                    cur.execute(sql, {**binds, "rc": rc})
                    result = rc.getvalue()
                    if result is None:
                        raise RunnerError("PLSQL_NO_CURSOR", "Procedure :rc cursor-ийг нээгээгүй (OPEN :rc FOR ...)")
                    result.arraysize = 5000
                else:
                    cur.execute(sql, binds)
                    result = cur
                cols = [d[0].upper() for d in result.description]
                types = [oracle_to_ch_type(d[1], d[4], d[5]) for d in result.description]
                rows = result.fetchall()
        finally:
            # Timeout-ийн дараа холболт тасардаг: тасарсан холболтод call_timeout оноовол python-oracledb процессыг
            # бүхэлд нь унагадаг (SIGBUS) тул зөвхөн эрүүл үед. Анхны алдаа (timeout) хэвээр үлдэнэ.
            if self._healthy():
                self.conn.call_timeout = 0
                self.conn.rollback()
        return cols, types, rows

    def _healthy(self) -> bool:
        try:
            return bool(self.conn.is_healthy())
        except Exception:  # noqa: BLE001
            return False

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


class ClickHouseConnector(Connector):
    """Source (read_only=True: readonly=2) болон үр дүнгийн store. Параметрийг SQL-д {p_report_date:Date} хэлбэрээр."""
    type = "clickhouse"

    def __init__(self, name: str, cfg: dict, read_only: bool = False):
        try:
            import clickhouse_connect
        except ImportError as exc:
            raise ConfigError("clickhouse-connect суугаагүй: pip install -r requirements.txt") from exc
        self.name = name
        self.read_only = read_only
        kwargs = dict(host=cfg["host"], port=int(cfg.get("port", 8123)),
                      username=cfg.get("user", "default"), password=cfg.get("password", ""),
                      secure=str(cfg.get("secure", False)).lower() == "true")
        try:
            self.client = clickhouse_connect.get_client(database=cfg.get("database", "default"), **kwargs)
        except Exception as exc:
            # risk_assessment database анх удаа үүсээгүй байж болно → default-аар холбогдоно
            if "UNKNOWN_DATABASE" not in str(exc) and "Code: 81" not in str(exc):
                raise
            self.client = clickhouse_connect.get_client(database="default", **kwargs)

    def query_typed(self, sql, params, timeout=None):
        if is_plsql_block(sql):
            raise RunnerError("PLSQL_NOT_SUPPORTED", f"{self.name}: procedure блок зөвхөн Oracle connection-д ажиллана")
        settings = {"max_execution_time": int(timeout)} if timeout else {}
        if self.read_only:
            settings["readonly"] = 2        # 2: SELECT + тохиргоо солих л болно, INSERT/DDL хориотой
        # Зөвхөн SQL-д {name:Type} хэлбэрээр байгаа параметрийг өгнө (LIKE '%x%'-тэй зөрчилдөхгүй)
        used = set(re.findall(r"\{(\w+):", sql))
        binds = {k: v for k, v in params.items() if k in used} or None
        res = self.client.query(sql, parameters=binds, settings=settings or None)
        types = [nullable(t.name) for t in res.column_types]
        return [c.upper() for c in res.column_names], types, res.result_rows

    def _writable(self) -> None:
        if self.read_only:
            raise RunnerError("READ_ONLY", f"{self.name}: source connection — бичих эрхгүй (зөвхөн SELECT)")

    def execute(self, sql, params=None):
        self._writable()
        self.client.command(sql, parameters=params or None)

    def insert(self, database, table, columns, rows):
        self._writable()
        if rows:
            self.client.insert(table, rows, column_names=columns, database=database)

    def table_columns(self, database, table):
        return list(self.table_column_types(database, table))

    def table_column_types(self, database, table):
        _, rows = self.query("SELECT name, type FROM system.columns WHERE database = {d:String} "
                             "AND table = {t:String} ORDER BY position",
                             {"d": database, "t": table})
        return {r[0].lower(): r[1] for r in rows}

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass


CONNECTOR_TYPES: dict[str, type] = {
    "oracle": OracleConnector,
    "clickhouse": ClickHouseConnector,
}


# Listener түр татгалзсан (ачаалал, process дүүрсэн): дахин оролдоно
_TRANSIENT_CONNECT = ("DPY-6005", "ORA-12516", "ORA-12519", "ORA-12520", "ORA-12541", "Connection refused")
CONNECT_RETRIES = 4


def connect(cfg: EnvConfig, name: str, read_only: bool = False) -> Connector:
    """read_only=True: source (SQL ажиллуулах) — DB-д юу ч бичиж чадахгүй. Oracle үргэлж зөвхөн уншина.
    Холболт түр татгалзвал (ORA-12516 г.м.) 0.5, 1, 2 сек хүлээж дахин оролдоно."""
    settings = cfg.connection_settings(name)
    ctype = settings.get("type")
    if ctype not in CONNECTOR_TYPES:
        raise ConfigError(f"{name}: type '{ctype}' дэмжигдэхгүй ({', '.join(CONNECTOR_TYPES)})")
    for attempt in range(CONNECT_RETRIES):
        try:
            if ctype == "clickhouse":
                return CONNECTOR_TYPES[ctype](name, settings, read_only=read_only)
            return CONNECTOR_TYPES[ctype](name, settings)
        except Exception as exc:  # noqa: BLE001
            if attempt == CONNECT_RETRIES - 1 or not any(m in str(exc) for m in _TRANSIENT_CONNECT):
                raise
            time.sleep(0.5 * 2 ** attempt)
    raise AssertionError("unreachable")


class ConnectionPool:
    """Run-ий турш thread бүрт connection-ийг дахин ашиглана (тооцоолол бүрт шинээр нээхгүй).
    Oracle query бүр READ ONLY transaction + rollback тул дахин ашиглахад аюулгүй; тасарсан (is_healthy = False)
    бол шинээр нээнэ."""

    def __init__(self, cfg: EnvConfig):
        self.cfg = cfg
        self._local = threading.local()
        self._all: list = []
        self._lock = threading.Lock()

    def get(self, name: str, read_only: bool = False) -> Connector:
        cache = getattr(self._local, "cache", None)
        if cache is None:
            cache = self._local.cache = {}
        key = (name, read_only)
        conn = cache.get(key)
        if conn is not None and not _healthy(conn):
            try:
                conn.close()
            except Exception:  # noqa: BLE001
                pass
            conn = None
        if conn is None:
            conn = cache[key] = connect(self.cfg, name, read_only=read_only)
            with self._lock:
                self._all.append(conn)
        return conn

    def close(self) -> None:
        with self._lock:
            conns, self._all = self._all, []
        for c in conns:
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass


def _healthy(conn: Connector) -> bool:
    raw = getattr(conn, "conn", None)
    try:
        return raw is None or not hasattr(raw, "is_healthy") or bool(raw.is_healthy())
    except Exception:  # noqa: BLE001
        return False


def classify_error(exc: Exception) -> tuple[str, str]:
    """(error_code, message). Timeout бол 'TIMEOUT'."""
    msg = str(exc).strip() or exc.__class__.__name__
    if isinstance(exc, RunnerError):
        return exc.code, msg
    if isinstance(exc, ConfigError):
        return "CONFIG_ERROR", msg
    if any(m in msg for m in _TIMEOUT_MARKERS):
        return "TIMEOUT", msg
    if any(m in msg for m in _READ_ONLY_MARKERS):
        return "SOURCE_WRITE_BLOCKED", (f"Source DB-д бичих оролдлого хориглогдлоо — код (procedure ч) зөвхөн уншина, "
                                        f"үр дүнг runner ClickHouse-д бичнэ: {msg}")
    m = _ERROR_CODE_RE.search(msg)
    return (m.group(1).replace("Code: ", "CH-") if m else "SQL_ERROR"), msg
