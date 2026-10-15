"""activities/ уншина: үйл ажиллагаа, үзүүлэлт, нийтлэг тооцоолол (_shared).

Бүтэц (давхардалгүй: master-ийн 1,380 мөр → ~500 тодорхойлолт):
  activities/_shared/sh_NNN.sql             — ОЛОН үйл ажиллагаанд давтагддаг үзүүлэлтийн НЭГ тодорхойлолт (нэр,
                                              аргачлал, шатлал, хугацаа + SQL эсвэл manual: true)
  activities/act_GG_slug/activity.yaml      — бүлэг GG, BRANCHID, нэр + `shared:` — нийтлэг тодорхойлолтын мөрүүд:
                                              {id: RI_40_1545, def: SH_007, weight: 1.5} (жин; зөрүүтэй бол
                                              шатлал / хугацаа / аргачлал энд)
  activities/act_GG_slug/ri_GG_NNNN.sql     — ЗӨВХӨН энэ үйл ажиллагааны үзүүлэлт (NNNN = master-ийн №)

Үзүүлэлтийн горим (mode):
  sql     — доор нь өөрийн SQL (эсвэл sql_from)
  shared  — нийтлэг тодорхойлолтын SQL-ийг НЭГ удаа ажиллуулж, SOL мөрүүдийг өөрийн үйл ажиллагааны
            SOL-уудаар нэгтгэнэ (activity.yaml shared:, эсвэл файлд `calc: SH_001`)
  manual  — хүн үнэлнэ (ri.py manual), SQL-гүй (`manual: true` эсвэл SQL-гүй нийтлэг тодорхойлолт)

Файлын эхэнд тохиргоо YAML-аар:
    /*---
    indicator_id: RI_01_0002
    name_mn: Зээлийн төлөвлөгөөний биелэлт
    weight: 1.5
    scale_text: "1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош"
    status: IN_PROGRESS
    version: 0.1.0
    ---*/
    SELECT ...
"""
import dataclasses
import datetime as dt
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import ACTIVITIES_DIR
from .scale import parse_scale_text

ACTIVITY_DIR_RE = re.compile(r"^act_(\d{2})_[a-z0-9]+(?:_[a-z0-9]+)*$")
SHARED_DIR = "_shared"
INDICATOR_ID_RE = re.compile(r"^RI_(\d{2})_(\d{4})$")      # бүлэг + master-ийн №
CALC_ID_RE = re.compile(r"^SH_(\d{3})$")
INDICATOR_FILE_RE = re.compile(r"^ri_\d{2}_\d{4}\.sql$")
CALC_FILE_RE = re.compile(r"^sh_\d{3}\.sql$")
FRONT_MATTER_RE = re.compile(r"^\s*/\*---[ \t]*\n(.*?)\n---\*/[ \t]*\n?", re.S)

STATUSES = ("TODO", "IN_PROGRESS", "REVIEW", "TESTED", "DONE")
FREQUENCIES = ("daily", "semimonthly", "monthly", "quarterly", "yearly")
COMPLEXITIES = ("simple", "medium", "complex")
MODES = ("sql", "shared", "manual")
# Хамрах хугацаа (master-ийн "Хамрах хугацаа" → runner-ийн :p_period_start):
#   report       тайлант хугацаа (-p / --from / period.yaml, эсвэл frequency)
#   last_year    сүүлийн 1 жил (тайлант өдрөөс 12 сар)
#   since_audit  үйл ажиллагааны сүүлийн аудитаас хойш (activity_map.csv LAST_AUDIT_DATE); :p_quarters = улирлын тоо
#   latest       тайлант өдрийн байдлаар хамгийн сүүлийн (үнэлгээ, шалгалт) — SQL :p_report_date-ээр
PERIODS = ("report", "last_year", "since_audit", "latest")
# `period:` бичээгүй бол master-ийн period_text-ээс (эхний таарсан)
PERIOD_PATTERNS = (
    ("since_audit", re.compile(r"аудит\w*\s+(орс\w*|хийгдсэн\w*)|аудитаас\s+хойш|өмнөх\s+аудитаас", re.I)),
    ("last_year", re.compile(r"сүүлийн\s+(1|нэг)\s+жил|сүүлийн\s+12\s+сар", re.I)),
    ("latest", re.compile(r"сүүлийн\s+үнэлгээ|хамгийн\s+сүүлд|сүүлд\s+авсан", re.I)),
)


def infer_period(period_text: str | None) -> str:
    """master-ийн "Хамрах хугацаа" → PERIODS: "Сүүлийн 1 жил" → last_year, "Аудит орсноос хойш…" → since_audit,
    "Сүүлийн үнэлгээгээр" / "Хамгийн сүүлд авсан шалгалтаар" → latest, бусад ("Тайлант хугацаагаар") → report."""
    for period, rx in PERIOD_PATTERNS:
        if rx.search(str(period_text or "")):
            return period
    return "report"
REQUIRED_FIELDS = ("indicator_id", "name_mn", "status", "version")
INHERITED = ("connection", "owner", "reviewer", "frequency", "timeout_seconds")


@dataclass
class Activity:
    activity_id: str
    group_no: int
    folder: Path
    name_mn: str
    name_en: str
    owner: str
    reviewer: str
    branch_id: str
    example: bool
    defaults: dict
    name_old: str = ""
    last_audit_date: dt.date | None = None     # "Аудит орсноос хойш" хугацааны эхлэл


@dataclass
class Indicator:
    indicator_id: str
    activity_id: str
    folder: Path
    name_mn: str
    name_en: str
    description: str
    owner: str
    reviewer: str
    connection: str
    frequency: str
    execution_order: int
    dependencies: list
    enabled: bool
    timeout_seconds: int
    status: str
    version: str
    complexity: str
    test_dates: list
    empty_source: str
    example: bool
    mode: str = "sql"                     # sql / shared / manual
    is_calc: bool = False                 # _shared/sh_NNN.sql (нийтлэг тодорхойлолт)
    calc: str | None = None               # shared горимд: SH_NNN
    weight: float | None = None           # үйл ажиллагаа доторх жин (%)
    score_type: str = ""
    scale: dict | None = None             # DaHUB score_scale
    scale_text: str = ""
    scale_error: str | None = None
    value_unit: str = "ratio"             # ratio (0.9746) | percent (97.46)
    score_metric: str = "value"
    automatable: str = ""
    master: dict = field(default_factory=dict)   # master-ийн мэдээллийн талбарууд
    value_range: dict | None = None       # {min, max} — VALUE-д
    sql_from: str | None = None
    params: dict = field(default_factory=dict)
    sql_override: Path | None = None
    check_sql: str | None = None
    source_check: str | None = None
    min_rows: int | None = None
    max_change_pct: dict | None = None    # {pct: 30}
    rollup_metrics: dict = field(default_factory=dict)  # {metric: sum|ratio}
    period: str = "report"                # PERIODS-ийн нэг
    period_explicit: bool = False         # period / period_text бичсэн (shared горимд calc-ийнхыг өвлөхгүй)
    def_id: str | None = None             # нийтлэг тодорхойлолт (SH_NNN) — activity.yaml shared: мөр
    manifest: dict | None = None          # activity.yaml-ийн мөр (sql_version, дарсан утга)
    def_path: Path | None = None          # тодорхойлолтын файл (ri_result.file_name)
    indicator_no: str = ""                # харуулах дугаар: "1.2" = 1-р үйл ажиллагааны 2-р үзүүлэлт
    sort_order: int = 0
    errors: list = field(default_factory=list)

    @property
    def file_stem(self) -> str:
        return self.indicator_id.lower()

    @property
    def file_path(self) -> Path:
        """Тохиргоо нь байгаа файл: өөрийн .sql, эсвэл activity.yaml (shared: мөр)."""
        if self.manifest is not None:
            return self.folder / "activity.yaml"
        return self.folder / f"{self.file_stem}.sql"

    @property
    def sql_path(self) -> Path:
        return self.sql_override or self.file_path

    def read_sql(self) -> str:
        return split_front_matter(self.sql_path.read_text(encoding="utf-8"))[1]

    @property
    def file_name(self) -> str:
        """ri_result.file_name: SQL / тодорхойлолт байгаа файл — activities/act_GG_slug/ri_GG_NNNN.sql эсвэл
        activities/_shared/sh_NNN.sql (нийтлэг)."""
        path = self.def_path or self.file_path
        return f"{path.parent.parent.name}/{path.parent.name}/{path.name}"

    @property
    def sql_version(self) -> str:
        """version + hash(файл бүтнээрээ (тохиргоо + SQL), sql_from-ийн SQL, задалсан {{shared.x}}).

        Shared горимд calc-ийн файл тусдаа (calc_version) — runner хоёуланг нь audit-д бичнэ.
        """
        from .sqltext import expand_shared
        h = hashlib.sha1()
        if self.manifest is not None:              # activity.yaml-ийн мөр: дарсан утгууд (SQL нь тодорхойлолтод)
            import json
            h.update(json.dumps(self.manifest, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8"))
            return f"{self.version}+{h.hexdigest()[:8]}"
        try:
            h.update(self.file_path.read_bytes().replace(b"\r\n", b"\n"))   # Windows (CRLF) / Linux ижил хувилбар
            body = self.read_sql() if self.mode == "sql" or self.is_calc else ""
            if body.strip():
                h.update(body.encode("utf-8"))
                h.update(expand_shared(body).encode("utf-8"))
        except (OSError, ValueError, Exception):  # noqa: BLE001 — shared алга г.м. (check мэдэгдэнэ)
            return f"{self.version}+nosql"
        return f"{self.version}+{h.hexdigest()[:8]}"

    @property
    def scale_version(self) -> str:
        import json
        raw = json.dumps(self.scale, sort_keys=True, ensure_ascii=False) + f"|{self.weight}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]

    @property
    def calc_id(self) -> str:
        """Тооцоолол / тодорхойлолтын ID: нийтлэг бол SH_NNN (гарын ч), эс бөгөөс өөрөө."""
        return self.calc or self.def_id or self.indicator_id


class Catalog:
    def __init__(self):
        self.activities: dict[str, Activity] = {}
        self.indicators: dict[str, Indicator] = {}
        self.calcs: dict[str, Indicator] = {}
        self.errors: list[str] = []

    def by_activity(self, activity_id: str) -> list[Indicator]:
        return sorted((i for i in self.indicators.values() if i.activity_id == activity_id),
                      key=lambda i: i.indicator_id)

    def resolve_activity(self, key) -> "Activity":
        """BRANCHID (998), ACT_01, 01, 1 — аль нь ч байж болно. Олдохгүй бол ValueError."""
        k = str(key).strip().upper()
        if k in self.activities:
            return self.activities[k]
        by_branch = [a for a in self.activities.values() if a.branch_id and a.branch_id == k]
        if by_branch:
            return by_branch[0]
        if k.isdigit() and len(k) <= 2 and f"ACT_{int(k):02d}" in self.activities:
            return self.activities[f"ACT_{int(k):02d}"]
        raise ValueError(f"Үйл ажиллагаа олдсонгүй: {key} (BRANCHID эсвэл ACT_NN)")

    def by_branch(self, branch_id) -> list[Indicator]:
        return self.by_activity(self.resolve_activity(branch_id).activity_id)

    def get(self, any_id: str) -> Indicator | None:
        return self.indicators.get(any_id) or self.calcs.get(any_id)


def apply_env_params(cat: Catalog, cfg) -> None:
    """config/<env>.yaml-ийн `params: {RI_01_0002: {p_pkeys: "10001,10002"}}` — орчин бүрт өөр параметр
    (жнь BI тайлангийн PKEY). Файлын params-ийг дарна; байхгүй үзүүлэлт бол catalog-ийн алдаа."""
    for iid, ps in ((getattr(cfg, "raw", None) or {}).get("params") or {}).items():
        ind = cat.get(str(iid).upper())
        if ind is None:
            cat.errors.append(f"config/{cfg.env}.yaml params: {iid} үзүүлэлт олдсонгүй")
        elif not isinstance(ps, dict) or not all(re.match(r"^p_[a-z0-9_]+$", str(k)) for k in ps):
            cat.errors.append(f"config/{cfg.env}.yaml params.{iid} нь {{p_name: утга}} хэлбэртэй")
        else:
            ind.params = {**ind.params, **ps}


def split_front_matter(text: str) -> tuple[str | None, str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _read_yaml(path: Path, errors: list) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{path}: YAML алдаа: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: YAML нь key: value бүтэцтэй байх ёстой")
        return None
    return data


def _as_date_list(values, errors, where) -> list:
    out = []
    for v in values or []:
        if isinstance(v, dt.date):
            out.append(v)
        else:
            try:
                out.append(dt.date.fromisoformat(str(v)))
            except ValueError:
                errors.append(f"{where}: test_dates-ийн утга буруу: {v}")
    return out


def _weight(v):
    if v is None or v == "":
        return None
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(v))
    return float(m.group().replace(",", ".")) if m else None


def load_catalog(root: Path = ACTIVITIES_DIR) -> Catalog:
    from .orgmap import group_to_audit, group_to_branch
    cat = Catalog()
    if not root.exists():
        cat.errors.append(f"{root} folder алга")
        return cat
    gmap = group_to_branch() if root == ACTIVITIES_DIR else {}
    audit_dates = group_to_audit() if root == ACTIVITIES_DIR else {}

    shared = root / SHARED_DIR
    if shared.is_dir():
        shared_act = Activity("SHARED", 0, shared, "Нийтлэг тооцоолол", "Shared", "", "", "", False, {})
        for path in sorted(shared.iterdir()):
            if path.name.startswith("."):
                continue
            if not CALC_FILE_RE.match(path.name):
                cat.errors.append(f"{path}: _shared дотор зөвхөн sh_NNN.sql байна")
                continue
            _load_file(cat, shared_act, path, is_calc=True)

    for folder in sorted(p for p in root.iterdir() if p.is_dir() and p.name != SHARED_DIR):
        m = ACTIVITY_DIR_RE.match(folder.name)
        if not m:
            cat.errors.append(f"{folder.name}: folder нэр act_NN_english_snake_case байх ёстой")
            continue
        act_yaml = folder / "activity.yaml"
        if not act_yaml.exists():
            cat.errors.append(f"{folder.name}: activity.yaml алга")
            continue
        a = _read_yaml(act_yaml, cat.errors)
        if a is None:
            continue
        expected_id = f"ACT_{m.group(1)}"
        if a.get("activity_id") != expected_id:
            cat.errors.append(f"{act_yaml}: activity_id нь {expected_id} байх ёстой (одоо: {a.get('activity_id')})")
            continue
        if expected_id in cat.activities:
            cat.errors.append(f"{folder.name}: {expected_id} давхардсан")
            continue
        if not a.get("activity_name_mn"):
            cat.errors.append(f"{act_yaml}: 'activity_name_mn' хоосон")
        group_no = int(m.group(1))
        defaults = dict(a.get("defaults") or {})
        defaults.setdefault("owner", a.get("owner"))
        defaults.setdefault("reviewer", a.get("reviewer"))
        branch = str(a.get("branch_id") or gmap.get(group_no) or "")
        act = Activity(expected_id, group_no, folder, a.get("activity_name_mn", ""),
                       a.get("activity_name_en", "") or "", a.get("owner", "") or "",
                       a.get("reviewer", "") or "", branch, bool(a.get("example", False)), defaults)
        act.name_old = str(a.get("activity_name_mn_old") or "")
        audit = a.get("last_audit_date") or audit_dates.get(group_no)
        if audit:
            try:
                act.last_audit_date = audit if isinstance(audit, dt.date) else dt.date.fromisoformat(str(audit))
            except ValueError:
                cat.errors.append(f"{act_yaml}: last_audit_date буруу: {audit}")
        cat.activities[expected_id] = act
        for path in sorted(folder.iterdir()):
            if path.name == "activity.yaml" or path.name.startswith("."):
                continue
            if not INDICATOR_FILE_RE.match(path.name):
                cat.errors.append(f"{path}: зөвхөн activity.yaml болон ri_GG_NNNN.sql байна")
                continue
            _load_file(cat, act, path)
        _load_manifest(cat, act, act_yaml, a.get("shared"))

    # Харуулах дугаар: үйл ажиллагаа доторх дараалал (master-ийн №-ээр) → 1.1, 1.2 ...; нэмэлт (9001+) → 1.Н1
    for act in cat.activities.values():
        k = n_extra = 0
        for ind in cat.by_activity(act.activity_id):
            num = int(ind.indicator_id[-4:])
            if num >= 9000:
                n_extra += 1
                ind.indicator_no, ind.sort_order = f"{act.group_no}.Н{n_extra}", 9000 + n_extra
            else:
                k += 1
                ind.indicator_no, ind.sort_order = f"{act.group_no}.{k}", k

    for ind in [*cat.calcs.values(), *cat.indicators.values()]:
        if ind.mode == "shared" and not ind.is_calc:
            calc = cat.calcs.get(ind.calc)
            if calc is None:
                ind.errors.append(f"{ind.indicator_id}: calc {ind.calc} (_shared) олдсонгүй")
            else:
                ind.connection = calc.connection
                ind.frequency = ind.frequency or calc.frequency
                if not ind.period_explicit:          # master-ийн "Хамрах хугацаа" хоосон → тооцооллынх
                    ind.period = calc.period
        if ind.sql_from:
            src = cat.indicators.get(ind.sql_from) or cat.calcs.get(ind.sql_from)
            if src is None:
                ind.errors.append(f"{ind.indicator_id}: sql_from {ind.sql_from} олдсонгүй")
            elif src.sql_from:
                ind.errors.append(f"{ind.indicator_id}: sql_from {ind.sql_from} нь өөрөө sql_from-той")
            else:
                ind.sql_override = src.sql_path
                if ind.is_calc and ind.mode == "manual":
                    ind.mode = "sql"
    return cat


# activity.yaml shared: мөрийн түлхүүрүүд (id, def, weight заавал; бусад нь тодорхойлолтыг дарна)
MANIFEST_KEYS = {"id", "def", "weight", "score_type", "scale_text", "scale", "period", "period_text", "method",
                 "required_info", "source_system", "automatable", "enabled", "params", "note"}


def _load_manifest(cat: Catalog, act: Activity, path: Path, entries) -> None:
    """activity.yaml `shared:` — нийтлэг тодорхойлолтын мөр бүрээс энэ үйл ажиллагааны үзүүлэлт (RI_GG_NNNN)."""
    if not entries:
        return
    where = f"{path.parent.name}/activity.yaml"
    if not isinstance(entries, list):
        cat.errors.append(f"{where}: shared нь жагсаалт ([{{id: RI_40_1545, def: SH_007, weight: 1.5}}, …])")
        return
    for e in entries:
        if not isinstance(e, dict) or not e.get("id") or not e.get("def"):
            cat.errors.append(f"{where}: shared мөр {{id, def, weight}} хэлбэртэй байх ёстой: {e}")
            continue
        iid = str(e["id"]).upper()
        m = INDICATOR_ID_RE.match(iid)
        if not m or int(m.group(1)) != act.group_no:
            cat.errors.append(f"{where}: id {iid} нь RI_{act.group_no:02d}_NNNN байх ёстой")
            continue
        if iid in cat.indicators or iid in cat.calcs:
            cat.errors.append(f"{where}: {iid} давхардсан (файл эсвэл өөр мөр)")
            continue
        d = cat.calcs.get(str(e["def"]).upper())
        if d is None:
            cat.errors.append(f"{where}: {iid} — def {e['def']} (activities/_shared) олдсонгүй")
            continue
        errs = list(d.errors)
        extra = sorted(set(e) - MANIFEST_KEYS)
        if extra:
            errs.append(f"{where} {iid}: мэдэгдэхгүй түлхүүр {extra}")
        if e.get("weight") in (None, "") and not act.example:
            errs.append(f"{where} {iid}: weight заавал")
        scale, scale_text, scale_err = d.scale, d.scale_text, d.scale_error
        if isinstance(e.get("scale"), dict):
            scale, scale_err = e["scale"], None
        elif e.get("scale_text") or isinstance(e.get("scale"), str):
            scale_text = str(e.get("scale_text") or e.get("scale"))
            scale, scale_err = parse_scale_text(scale_text)
        master = dict(d.master)
        for k in ("method", "period_text", "required_info", "source_system"):
            if e.get(k):
                master[k] = str(e[k])
        if e.get("period"):
            period, explicit = str(e["period"]), True
        elif e.get("period_text"):
            period, explicit = infer_period(e["period_text"]), True
        else:
            period, explicit = d.period, d.period_explicit
        if period not in PERIODS:
            errs.append(f"{where} {iid}: period нь {PERIODS}-ийн нэг")
            period = "report"
        params = e.get("params") or {}
        if not isinstance(params, dict):
            errs.append(f"{where} {iid}: params нь {{p_name: утга}}")
            params = {}
        ind = dataclasses.replace(
            d, indicator_id=iid, activity_id=act.activity_id, folder=act.folder, owner=act.owner,
            reviewer=act.reviewer, example=act.example, is_calc=False,
            mode="manual" if d.mode == "manual" else "shared", calc=None if d.mode == "manual" else d.indicator_id,
            def_id=d.indicator_id, manifest=dict(e), def_path=d.file_path, sql_override=None, sql_from=None,
            weight=_weight(e.get("weight")), score_type=str(e.get("score_type") or d.score_type),
            scale=scale, scale_text=scale_text, scale_error=scale_err, master=master,
            automatable=str(e.get("automatable") or d.automatable),
            period=period, period_explicit=explicit, enabled=bool(e.get("enabled", True)) and d.enabled,
            params=params, errors=errs, test_dates=list(d.test_dates),       # params: зөвхөн энэ мөрийн (+ тодорхойлолтынх)
            dependencies=list(d.dependencies))
        cat.indicators[iid] = ind


def _load_file(cat: Catalog, act: Activity, path: Path, is_calc: bool = False) -> None:
    errs: list[str] = []
    meta_text, body = split_front_matter(path.read_text(encoding="utf-8"))
    if meta_text is None:
        cat.errors.append(f"{path}: файлын эхэнд /*--- ... ---*/ тохиргоо алга")
        return
    try:
        d = yaml.safe_load(meta_text)
    except yaml.YAMLError as exc:
        cat.errors.append(f"{path}: тохиргооны YAML алдаа: {exc}")
        return
    if not isinstance(d, dict):
        cat.errors.append(f"{path}: тохиргоо нь key: value бүтэцтэй байх ёстой")
        return
    d.setdefault("name_mn", d.get("indicator_name_mn"))
    ind_id = d.get("indicator_id")
    expected = path.stem.upper()
    if ind_id != expected:
        cat.errors.append(f"{path}: indicator_id нь {expected} байх ёстой (одоо: {ind_id})")
        return
    if ind_id in cat.indicators or ind_id in cat.calcs:
        cat.errors.append(f"{path}: {ind_id} давхардсан")
        return

    where = f"{path.parent.name}/{path.name}"
    for f in REQUIRED_FIELDS:
        if d.get(f) in (None, ""):
            errs.append(f"{where}: '{f}' заавал")
    if not is_calc:
        if d.get("activity_id", act.activity_id) != act.activity_id:
            errs.append(f"{where}: activity_id {act.activity_id} байх ёстой")
        if INDICATOR_ID_RE.match(ind_id).group(1) != act.activity_id[-2:]:
            errs.append(f"{where}: ID-ийн бүлгийн дугаар folder-той таарахгүй")

    has_sql = bool(body.strip())
    calc = d.get("calc")
    manual = bool(d.get("manual", False))
    sql_from = d.get("sql_from")
    if is_calc:
        mode = "manual" if manual else "sql"        # нийтлэг тодорхойлолт: SQL-тэй эсвэл гарын
    elif calc:
        mode = "shared"
    elif manual:
        mode = "manual"
    else:
        mode = "sql"
    if calc and not CALC_ID_RE.match(str(calc)):
        errs.append(f"{where}: calc нь SH_NNN байх ёстой")
    if mode in ("shared", "manual") and has_sql:
        errs.append(f"{where}: {mode} горимд доор нь SQL бичихгүй")
    if mode == "sql" and not sql_from and not has_sql:
        errs.append(f"{where}: тохиргооны доор SQL алга (эсвэл manual: true / calc: SH_NNN)")
    if sql_from and has_sql:
        errs.append(f"{where}: sql_from-той үед доор нь SQL бичихгүй")

    merged = {k: d.get(k, act.defaults.get(k)) for k in INHERITED}
    if mode == "sql" and not merged["connection"]:
        errs.append(f"{where}: connection заагаагүй")
    if merged["frequency"] and merged["frequency"] not in FREQUENCIES:
        errs.append(f"{where}: frequency нь {FREQUENCIES}-ийн нэг байх ёстой")
    if d.get("status") not in STATUSES:
        errs.append(f"{where}: status нь {STATUSES}-ийн нэг байх ёстой")
    complexity = d.get("complexity", "simple")
    if complexity not in COMPLEXITIES:
        errs.append(f"{where}: complexity нь {COMPLEXITIES}-ийн нэг байх ёстой")
    empty_source = d.get("empty_source", "warn")
    if empty_source not in ("warn", "fail"):
        errs.append(f"{where}: empty_source нь warn эсвэл fail")
    deps = d.get("dependencies") or []
    if not isinstance(deps, list):
        errs.append(f"{where}: dependencies нь жагсаалт байх ёстой")
        deps = []
    vr = d.get("value_range")
    if vr is not None and not (isinstance(vr, dict) and set(vr) <= {"min", "max"}):
        errs.append(f"{where}: value_range нь {{min: .., max: ..}} хэлбэртэй")
        vr = None
    params = d.get("params") or {}
    if not isinstance(params, dict) or not all(re.match(r"^p_[a-z0-9_]+$", str(k)) for k in params):
        errs.append(f"{where}: params нь {{p_name: утга}} хэлбэртэй")
        params = {}
    for key in ("check_sql", "source_check"):
        if d.get(key) is not None and not isinstance(d.get(key), str):
            errs.append(f"{where}: {key} нь SQL текст (|) байх ёстой")
            d[key] = None
    min_rows = d.get("min_rows")
    if min_rows is not None and (not isinstance(min_rows, int) or min_rows < 1):
        errs.append(f"{where}: min_rows нь эерэг бүхэл тоо байх ёстой")
        min_rows = None
    mcp = d.get("max_change_pct")
    if mcp is not None:
        pct = mcp.get("pct") if isinstance(mcp, dict) else mcp
        if not isinstance(pct, (int, float)):
            errs.append(f"{where}: max_change_pct нь {{pct: 30}} эсвэл тоо")
            mcp = None
        else:
            mcp = {"pct": float(pct)}

    # Оноо: scale (DaHUB JSON) эсвэл scale_text (master-ийн текст)
    scale, scale_err = d.get("scale"), None
    scale_text = str(d.get("scale_text") or "")
    if isinstance(scale, str):
        scale_text, scale = scale, None
    if scale is not None and not isinstance(scale, dict):
        errs.append(f"{where}: scale нь DaHUB-ийн score_scale (dict) эсвэл текст")
        scale = None
    if scale is None and scale_text.strip():
        scale, scale_err = parse_scale_text(scale_text)
    value_unit = d.get("value_unit", "ratio")
    if value_unit not in ("ratio", "percent"):
        errs.append(f"{where}: value_unit нь ratio эсвэл percent")
        value_unit = "ratio"
    period = str(d.get("period") or infer_period(d.get("period_text")))
    if period not in PERIODS:
        errs.append(f"{where}: period нь {PERIODS}-ийн нэг")
        period = "report"
    rollup = d.get("rollup_metrics") or {}
    if not isinstance(rollup, dict) or not all(v in ("sum", "ratio") for v in rollup.values()):
        errs.append(f"{where}: rollup_metrics нь {{metric: sum|ratio}}")
        rollup = {}

    obj = Indicator(
        indicator_id=ind_id,
        activity_id=act.activity_id,
        folder=act.folder,
        name_mn=d.get("name_mn") or "",
        name_en=d.get("name_en") or "",
        description=d.get("description") or d.get("method") or "",
        owner=merged["owner"] or "",
        reviewer=merged["reviewer"] or "",
        connection=merged["connection"] or "",
        frequency=merged["frequency"] or "quarterly",
        execution_order=int(d.get("execution_order", 100)),
        dependencies=[str(x) for x in deps],
        enabled=bool(d.get("enabled", True)),
        timeout_seconds=int(merged["timeout_seconds"] or 0),
        status=d.get("status", "TODO"),
        version=str(d.get("version", "0.0.0")),
        complexity=complexity,
        test_dates=_as_date_list(d.get("test_dates"), errs, where),
        empty_source=empty_source,
        example=act.example,
        mode=mode,
        is_calc=is_calc,
        calc=str(calc) if calc else None,
        weight=_weight(d.get("weight")),
        score_type=str(d.get("score_type") or ""),
        scale=scale,
        scale_text=scale_text,
        scale_error=scale_err,
        value_unit=value_unit,
        score_metric=str(d.get("score_metric") or "value"),
        automatable=str(d.get("automatable") or ""),
        master={k: d.get(k) for k in ("source_system", "required_info", "method", "period_text") if d.get(k)},
        value_range=vr,
        sql_from=str(sql_from) if sql_from else None,
        params=params,
        check_sql=d.get("check_sql"),
        source_check=d.get("source_check"),
        min_rows=min_rows,
        max_change_pct=mcp,
        rollup_metrics=rollup,
        period=period,
        period_explicit=bool(d.get("period") or str(d.get("period_text") or "").strip()),
        errors=errs,
    )
    (cat.calcs if is_calc else cat.indicators)[ind_id] = obj
