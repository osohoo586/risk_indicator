"""Үйл ажиллагаа (ACTIVITY) ↔ BRANCHID ↔ SOLID холбоо.

  SOLID     хамгийн жижиг нэгж: хэлтэс, салбар, алба, газар — SQL бүр энэ түвшинд тоолно
  BRANCHID  SOLID-уудыг нэгтгэх салбар/газар; үйл ажиллагаа бүр нэг BRANCHID-тай
  ACTIVITY  үйл ажиллагаа = үнэлгээ (master-ийн бүлэг); үзүүлэлтүүд нь энэ BRANCHID-ийн SOLID-уудаар нэгтгэгдэнэ

config/activity_map.csv   : GROUP_NO, MASTER_NAME, NAME_EN, BRANCHID, LAST_AUDIT_DATE, CONFIDENCE, NOTE
BRANCHID → SOLID:
  config/<env>.yaml-д org: {connection: oracle_whouse, shared: org.units} бол DB-ээс — shared/org/units.sql
      (SOLID, BRANCHID, SOLNAME) тайлант өдрөөр (:p_report_date). Бүтэц өөрчлөгдвөл автоматаар.
  эс бөгөөс config/activity_units.csv : BRANCHNAME, SOLID, BRANCHID, SUBBRANCHID, TDATE (snapshot)

Нэг SOL олон BRANCHID-д орж болно (жнь 809, 950). Тайлант огноо d-д: TDATE ≤ d хамгийн сүүлийн
snapshot-ыг ашиглана (d-ээс өмнөх snapshot байхгүй бол хамгийн эртнийхийг).

Аудитын огноо ("аудит орсноос хойш" хугацааны эхлэл):
  config/<env>.yaml-д audit: {connection: oracle_whouse, shared: grc.last_audit} бол DB-ээс — тайлант өдрөөс
      өмнөх сүүлийн аудит (BRANCHID, LAST_AUDIT_DATE). Шинэ аудит орвол автоматаар.
  эс бөгөөс activity_map.csv LAST_AUDIT_DATE (эсвэл activity.yaml last_audit_date).
"""
import csv
import datetime as dt
import threading
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from .config import CONFIG_DIR, PROJECT_ROOT
from .dates import to_date

# Орчин бүр өөр файл ашиглаж болно (local тест: tests/local/...). config/<env>.yaml:
#   orgmap: {activity_map: config/activity_map.csv, activity_units: tests/local/activity_units.csv}
_PATHS = {"activity_map": CONFIG_DIR / "activity_map.csv", "activity_units": CONFIG_DIR / "activity_units.csv"}


_DB: dict = {"cfg": None, "connection": None, "shared": "org.units"}
_DB_CACHE: dict = {}
_AUDIT: dict = {"cfg": None, "connection": None, "shared": "grc.last_audit"}
_AUDIT_CACHE: dict = {}
_LOCK = threading.Lock()


def use(cfg) -> None:
    """cfg.raw['orgmap'] (CSV файлууд), cfg.raw['org'] (DB)-ийг идэвхжүүлнэ."""
    raw = getattr(cfg, "raw", None) or {}
    conf = raw.get("orgmap") or {}
    new = {k: (PROJECT_ROOT / conf[k]) if conf.get(k) else CONFIG_DIR / f"{k}.csv" for k in _PATHS}
    if new != _PATHS:
        _PATHS.update(new)
        clear_cache()
    org = raw.get("org") or {}
    audit = raw.get("audit") or {}
    with _LOCK:
        _DB.update(cfg=cfg if org.get("connection") else None, connection=org.get("connection"),
                   shared=org.get("shared", "org.units"))
        _DB_CACHE.clear()
        _AUDIT.update(cfg=cfg if audit.get("connection") else None, connection=audit.get("connection"),
                      shared=audit.get("shared", "grc.last_audit"))
        _AUDIT_CACHE.clear()


def _query_shared(cfg, connection: str, shared: str, d: dt.date) -> tuple[list[str], list]:
    from .db import RunnerError, connect
    from .sqltext import clean_trailing, expand_shared, render_schemas, shared_path
    path = shared_path(shared)
    if not path.exists():
        raise RunnerError("ORG_UNITS", f"{path} алга (config {shared})")
    sql = clean_trailing(render_schemas(expand_shared(path.read_text(encoding="utf-8")), cfg.schemas))
    with connect(cfg, connection, read_only=True) as conn:
        cols, rows = conn.query(sql, {"p_report_date": d, "p_date_to": d})
    return [c.upper() for c in cols], rows


def audit_source() -> str:
    if _AUDIT["cfg"] is not None:
        return f"db ({_AUDIT['connection']}, shared/{_AUDIT['shared'].replace('.', '/')}.sql)"
    return f"{_PATHS['activity_map']} (LAST_AUDIT_DATE)"


def audit_date(act, d: dt.date) -> dt.date | None:
    """Үйл ажиллагааны тайлант өдрөөс өмнөх сүүлийн аудитын огноо (байхгүй бол None)."""
    if _AUDIT["cfg"] is None:
        a = getattr(act, "last_audit_date", None)
        return a if a and a <= d else None
    with _LOCK:
        if d not in _AUDIT_CACHE:
            cols, rows = _query_shared(_AUDIT["cfg"], _AUDIT["connection"], _AUDIT["shared"], d)
            i = {c: cols.index(c) for c in cols}
            _AUDIT_CACHE[d] = {_key(r[i["BRANCHID"]]): to_date(r[i["LAST_AUDIT_DATE"]]) for r in rows
                               if r[i["LAST_AUDIT_DATE"]] is not None}
        return _AUDIT_CACHE[d].get(str(act.branch_id))


def source() -> str:
    """BRANCHID → SOLID хаанаас: 'db (oracle_whouse, shared/org/units.sql)' эсвэл CSV зам."""
    if _DB["cfg"] is not None:
        return f"db ({_DB['connection']}, shared/{_DB['shared'].replace('.', '/')}.sql)"
    return str(_PATHS["activity_units"])


def _key(v) -> str:
    """SOLID/BRANCHID: 101, 101.0, Decimal('101'), ' 101 ' → '101'."""
    if v is None:
        return ""
    if isinstance(v, (int, float, Decimal)) and float(v).is_integer():
        return str(int(v))
    return str(v).strip()


def _db_units(d: dt.date) -> list[dict]:
    """Тайлант өдрийн SOLID → BRANCHID (DB, run-д өдөр бүрт нэг удаа)."""
    with _LOCK:
        if d in _DB_CACHE:
            return _DB_CACHE[d]
        from .db import RunnerError, connect
        from .sqltext import clean_trailing, expand_shared, render_schemas, shared_path
        cfg = _DB["cfg"]
        path = shared_path(_DB["shared"])
        if not path.exists():
            raise RunnerError("ORG_UNITS", f"{path} алга (config org.shared)")
        sql = clean_trailing(render_schemas(expand_shared(path.read_text(encoding="utf-8")), cfg.schemas))
        with connect(cfg, _DB["connection"], read_only=True) as conn:
            cols, rows = conn.query(sql, {"p_report_date": d, "p_date_to": d})
        cols = [c.upper() for c in cols]
        missing = {"SOLID", "BRANCHID"} - set(cols)
        if missing:
            raise RunnerError("ORG_UNITS", f"shared/{_DB['shared']}: {sorted(missing)} багана алга (SOLID, BRANCHID, SOLNAME)")
        i = {c: cols.index(c) for c in cols}
        out = [{"SOLID": _key(r[i["SOLID"]]), "BRANCHID": _key(r[i["BRANCHID"]]),
                "BRANCHNAME": str(r[i["SOLNAME"]] or "") if "SOLNAME" in i else ""} for r in rows
               if r[i["SOLID"]] is not None and r[i["BRANCHID"]] is not None]
        _DB_CACHE[d] = out
        return out


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


@lru_cache(maxsize=1)
def group_to_audit() -> dict[int, str]:
    """{бүлэг: сүүлийн аудитын огноо} — activity_map.csv LAST_AUDIT_DATE (байхгүй бол хоосон)."""
    return {int(r["GROUP_NO"]): r["LAST_AUDIT_DATE"] for r in _read(_PATHS["activity_map"])
            if r.get("GROUP_NO") and r.get("LAST_AUDIT_DATE")}


@lru_cache(maxsize=1)
def group_names_en() -> dict[int, str]:
    """{бүлэг: англи нэр} — activity_map.csv NAME_EN (import-д folder-ийн нэр)."""
    return {int(r["GROUP_NO"]): r["NAME_EN"] for r in _read(_PATHS["activity_map"])
            if r.get("GROUP_NO") and r.get("NAME_EN")}


@lru_cache(maxsize=1)
def group_to_branch() -> dict[int, str]:
    out = {}
    for r in _read(_PATHS["activity_map"]):
        if r.get("GROUP_NO") and r.get("BRANCHID"):
            out[int(r["GROUP_NO"])] = r["BRANCHID"]
    return out


@lru_cache(maxsize=1)
def _units() -> list[dict]:
    rows = []
    for r in _read(_PATHS["activity_units"]):
        if not r.get("SOLID") or not r.get("BRANCHID"):
            continue
        try:
            r["_date"] = to_date(r["TDATE"]) if r.get("TDATE") else dt.date.min
        except ValueError:
            r["_date"] = dt.date.min
        rows.append(r)
    return rows


def snapshot_date(d: dt.date) -> dt.date | None:
    dates = sorted({r["_date"] for r in _units()})
    if not dates:
        return None
    past = [x for x in dates if x <= d]
    return past[-1] if past else dates[0]


def sols_for(branch_id: str, d: dt.date) -> dict[str, str]:
    """{sol_id: sol_name} — тухайн огнооны бүтцээр (DB эсвэл CSV snapshot)."""
    if _DB["cfg"] is not None:
        return {r["SOLID"]: r["BRANCHNAME"] for r in _db_units(d) if r["BRANCHID"] == str(branch_id)}
    snap = snapshot_date(d)
    return {r["SOLID"]: r.get("BRANCHNAME", "") for r in _units()
            if r["BRANCHID"] == str(branch_id) and r["_date"] == snap}


def all_sols(d: dt.date) -> dict[str, str]:
    if _DB["cfg"] is not None:
        return {r["SOLID"]: r["BRANCHNAME"] for r in _db_units(d)}
    snap = snapshot_date(d)
    return {r["SOLID"]: r.get("BRANCHNAME", "") for r in _units() if r["_date"] == snap}


def clear_cache() -> None:
    group_to_audit.cache_clear()
    group_names_en.cache_clear()
    group_to_branch.cache_clear()
    _units.cache_clear()
