"""Static шалгалт: DB-гүйгээр metadata, SQL (SELECT / procedure блок), shared/-ийн стандартыг шалгана."""
import hashlib
import re
from graphlib import CycleError, TopologicalSorter

import yaml

from .config import CONFIG_DIR, SHARED_DIR, ConfigError, known_connections
from .metadata import STATUSES, Catalog, Indicator
from .sqltext import expand_shared, is_plsql_block, shared_path, shared_refs, strip_comments_and_strings

_RULES = [
    (re.compile(r"\bSELECT\s+(?:DISTINCT\s+)?\*", re.I), "SELECT * хориглоно, багануудыг нэрлэж бич"),
    (re.compile(r"\w\.\*"), "alias.* хориглоно, багануудыг нэрлэж бич"),
    (re.compile(r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|COMMIT|ROLLBACK)\b", re.I),
     "SQL зөвхөн SELECT эсвэл procedure дуудах блок байна (DML/DDL хориглоно)"),
    (re.compile(r"\b(EXECUTE\s+IMMEDIATE|DBMS_SQL|FOR\s+UPDATE|LOCK\s+TABLE|OPTIMIZE\s+TABLE|RENAME\s+TABLE|"
                r"EXCHANGE\s+TABLES|ATTACH|DETACH|KILL\s+QUERY|INTO\s+OUTFILE|"
                r"SYSTEM\s+(?:STOP|START|FLUSH|DROP|RELOAD|SYNC|RESTART))\b", re.I),
     "Source-ийг өөрчлөх/түгжих команд хориглоно — SQL зөвхөн уншина, үр дүнг runner бичнэ"),
    (re.compile(r"\b(password|passwd|pwd)\s*=", re.I), "Нууц үг SQL-д байж болохгүй"),
    (re.compile(r"\b\w+/\w+@[\w.\-]+"), "Connection string SQL-д байж болохгүй"),
    (re.compile(r"@\s*[A-Za-z_]\w*\b(?!\s*\()"), "DB link (@link) ашиглахгүй — config-ийн connection ашигла"),
]
_LITERAL_DATE = re.compile(r"(DATE\s*'\d{4}-\d{2}-\d{2}'|'\d{4}-\d{2}-\d{2}')", re.I)
_DATE_PARAM = re.compile(r":p_(report_date|period_start|period_end|prev_period_end|date_from|date_to)\b", re.I)
_CH_DATE_PARAM = re.compile(r"\{p_(report_date|period_start|prev_period_end|date_from|date_to)\w*:", re.I)
_CH_PARAM = re.compile(r"\{\s*(p_\w+)\s*:\s*\w")                  # ClickHouse: {p_report_date:Date}
_ORACLE_PARAM = re.compile(r"(?<![:\w]):(p_\w+|rc)\b", re.I)          # Oracle: :p_report_date, :rc
_SCHEMA_LITERAL = re.compile(r"\b(FINACLE|COREMIS|RISKASSESSMENT|GOLOMT_V1|CARDZONE|ERP)\.", re.I)


def dialect_errors(who: str, body: str, conn_type: str | None, conn: str) -> list[str]:
    """Параметрийн бичиглэл connection-ий DB-тэй таарах ёстой (comment, string хассан SQL)."""
    if conn_type == "clickhouse":
        bad = sorted({m.group(1) for m in _ORACLE_PARAM.finditer(body)})
        if bad:
            return [f"{who}: Oracle параметр (:{bad[0]}) ClickHouse connection ({conn})-д ажиллахгүй — "
                    f"{{{bad[0]}:Date}} / {{{bad[0]}:String}} гэж бичнэ, эсвэл Oracle connection сонгоно"]
    elif conn_type:
        bad = sorted({m.group(1) for m in _CH_PARAM.finditer(body)})
        if bad:
            return [f"{who}: ClickHouse параметр ({{{bad[0]}:...}}) Oracle connection ({conn})-д ажиллахгүй — "
                    f":{bad[0]} гэж бичнэ, эсвэл connection: clickhouse_... сонгоно"]
    return []


def _rule_errors(who: str, raw: str) -> tuple[list[str], list[str]]:
    """Нэг SQL текстийн (үзүүлэлт, нийтлэг тооцоолол эсвэл shared/ файл) дүрмийн шалгалт."""
    errors, warnings = [], []
    body = strip_comments_and_strings(raw)
    for rx, msg in _RULES:
        if rx.search(body):
            errors.append(f"{who}: {msg}")
    no_comments = re.sub(r"/\*.*?\*/", " ", raw, flags=re.S)
    no_comments = re.sub(r"--[^\n]*", " ", no_comments)
    if _LITERAL_DATE.search(no_comments):
        errors.append(f"{who}: Literal огноо хориглоно — :p_report_date, :p_period_start зэрэг параметр ашигла")
    if _SCHEMA_LITERAL.search(body) and "{{" not in body:
        warnings.append(f"{who}: schema нэрийг шууд бичсэн — орчин бүрд ижил биш бол {{{{schema.alias}}}} ашигла")
    if raw.rstrip().endswith(";") and not is_plsql_block(raw):
        warnings.append(f"{who}: төгсгөлийн ; хэрэггүй (runner автоматаар хасна)")
    return errors, warnings


def check_sql(ind: Indicator, conn_type: str | None) -> tuple[list[str], list[str]]:
    iid = ind.indicator_id
    try:
        raw = ind.read_sql()
    except OSError:
        return [f"{iid}: SQL файл уншиж чадсангүй"], []
    if not raw.strip():
        return [f"{iid}: SQL хоосон"], []
    errors, warnings = _rule_errors(iid, raw)
    missing = [n for n in shared_refs(raw) if not shared_path(n).exists()]
    for name in missing:
        errors.append(f"{iid}: {{{{shared.{name}}}}} — {shared_path(name).relative_to(SHARED_DIR.parent)} алга")
    if missing:
        return errors, warnings
    try:
        full = expand_shared(raw)
    except ConfigError as exc:
        errors.append(f"{iid}: {exc}")
        return errors, warnings
    body = strip_comments_and_strings(full)
    block = is_plsql_block(raw)
    errors += dialect_errors(iid, body, conn_type, ind.connection)
    if block:
        if conn_type and conn_type != "oracle":
            errors.append(f"{iid}: procedure блок зөвхөн Oracle connection-д ажиллана ({ind.connection})")
        if not re.search(r":rc\b", body, re.I):
            errors.append(f"{iid}: procedure блок үр дүнгээ :rc (SYS_REFCURSOR)-оор буцаана: "
                          f"BEGIN pkg.proc(..., :rc); END;")
    if conn_type == "clickhouse":
        if not _CH_DATE_PARAM.search(full):
            warnings.append(f"{iid}: огнооны параметр ({{p_report_date:Date}}) ашиглаагүй")
    elif not _DATE_PARAM.search(body) and ind.period != "latest":
        warnings.append(f"{iid}: огнооны параметр (:p_report_date / :p_period_start) ашиглаагүй")

    if "TODO" in strip_comments_and_strings(raw).upper() and STATUSES.index(ind.status) >= STATUSES.index("REVIEW"):
        errors.append(f"{iid}: status={ind.status} боловч SQL-д TODO үлдсэн")
    if re.search(r"\bAS\s+\"?(SOL_ID|BRANCH_ID|BALANCE_AMT|SCALE)\b", body, re.I) and \
            not re.search(r"\bENTITY_LEVEL\b", body, re.I):
        warnings.append(f"{iid}: хуучин баганын хэлбэр — ENTITY_LEVEL, ENTITY_ID, VALUE стандарт (docs/sql_standard.md)")
    if not block:                    # procedure cursor-ийн баганыг DB-гүйгээр мэдэх боломжгүй
        for col in ("ENTITY_LEVEL", "ENTITY_ID", "VALUE"):
            if not re.search(rf"\b{col}\b", body, re.I):
                errors.append(f"{iid}: стандарт багана {col} SQL-д алга")
    if re.search(r"\bri_result\b|\{\{\s*schema\.ri\s*\}\}", body, re.I) and not ind.dependencies:   # comment-гүй
        warnings.append(f"{iid}: өөр үзүүлэлтийн үр дүнг (ri_result) уншиж байна — dependencies: [RI_..] заана уу")
    return errors, warnings


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", strip_comments_and_strings(text)).strip().upper()


def check_shared() -> tuple[list[str], list[str]]:
    """shared/-ийн файл бүр: нэр стандарт, зөвхөн SELECT, дүрэм."""
    errors, warnings = [], []
    if not SHARED_DIR.exists():
        return errors, warnings
    for path in sorted(SHARED_DIR.rglob("*.sql")):
        rel = path.relative_to(SHARED_DIR)
        who = f"shared/{rel.as_posix()}"
        if not all(re.match(r"^[a-z][a-z0-9_]*$", p) for p in [*rel.parts[:-1], rel.stem]):
            errors.append(f"{who}: нэр жижиг үсэг, тоо, _ (жнь shared/erp/employee_sol.sql)")
            continue
        raw = path.read_text(encoding="utf-8")
        if is_plsql_block(raw):
            errors.append(f"{who}: shared-д зөвхөн SELECT (procedure блок биш)")
        e, w = _rule_errors(who, raw)
        errors += e
        warnings += w
    return errors, warnings


def _unused_shared(used: set[str]) -> list[str]:
    """Аль ч үзүүлэлт, shared файл, config (org, branch_list) иш татаагүй shared/ файлууд."""
    if not SHARED_DIR.exists():
        return []
    files = {".".join(p.relative_to(SHARED_DIR).with_suffix("").parts): p for p in sorted(SHARED_DIR.rglob("*.sql"))}
    used = set(used)
    for path in files.values():
        used.update(shared_refs(path.read_text(encoding="utf-8")))
    for path in CONFIG_DIR.glob("*.yaml"):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(raw, dict):
            for key in ("org", "audit", "branch_list"):
                if isinstance(raw.get(key), dict) and raw[key].get("shared"):
                    used.add(raw[key]["shared"])
    return [f"shared/{p.relative_to(SHARED_DIR).as_posix()}: аль ч үзүүлэлт ашиглаагүй"
            for name, p in files.items() if name not in used]


def run_checks(cat: Catalog, indicator_ids: list[str] | None = None) -> tuple[list[str], list[str]]:
    conns = known_connections()
    errors = list(cat.errors)        # YAML эвдэрсэн, нэр буруу файлууд — үргэлж харуулна
    warnings: list[str] = []
    targets = [cat.indicators[i] for i in (indicator_ids if indicator_ids is not None else sorted(cat.indicators))]

    for ind in targets:
        errors.extend(ind.errors)
        if conns and ind.connection and ind.connection not in conns:
            errors.append(f"{ind.indicator_id}: connection '{ind.connection}' config/*.yaml-д алга")
        for dep in ind.dependencies:
            if cat.get(dep) is None:
                errors.append(f"{ind.indicator_id}: dependency {dep} олдсонгүй")
            elif dep == ind.indicator_id:
                errors.append(f"{ind.indicator_id}: өөрөөсөө хамаарч болохгүй")
        if ind.sql_from:
            src = cat.get(ind.sql_from)
            if src and src.connection != ind.connection:
                errors.append(f"{ind.indicator_id}: sql_from {ind.sql_from}-тэй connection ижил байх ёстой")
        elif ind.mode == "sql" and ind.sql_path.exists():
            e, w = check_sql(ind, conns.get(ind.connection))
            errors.extend(e)
            warnings.extend(w)
        for key in ("source_check", "check_sql"):
            text = getattr(ind, key)
            if not text:
                continue
            body = strip_comments_and_strings(text)
            if re.search(r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|TRUNCATE|ALTER|CREATE)\b", body, re.I):
                errors.append(f"{ind.indicator_id}: {key} зөвхөн SELECT байна")
            if key == "source_check":
                errors += dialect_errors(f"{ind.indicator_id} source_check", body, conns.get(ind.connection),
                                         ind.connection)

    # Горим, оноо
    for ind in targets:
        todo = [k for k, v in ind.params.items() if str(v).strip().upper() == "TODO"]
        if todo and not ind.example:
            warnings.append(f"{ind.indicator_id}: params бөглөөгүй ({', '.join(todo)} = TODO) — ажиллахгүй")
        extra = ind.indicator_id[-4:] >= "9000"     # master-д байхгүй нэмэлт (9001+) — оноонд орохгүй
        if not ind.is_calc and ind.weight is None and not ind.example and not extra:
            warnings.append(f"{ind.indicator_id}: weight (жин %) алга — үйл ажиллагааны оноонд орохгүй")
        if not ind.is_calc and ind.scale_error:
            warnings.append(f"{ind.indicator_id}: scale_text задарсангүй ({ind.scale_error}) — "
                            f"scale: {{type, numericRules}} гараар бич")
        if not ind.is_calc and ind.mode != "manual" and not ind.scale and not ind.example and not extra:
            warnings.append(f"{ind.indicator_id}: шатлал (scale / scale_text) алга — оноо тооцогдохгүй")

    if indicator_ids is None:
        # Нийтлэг тодорхойлолт (_shared): SQL шалгалт (нэг удаа), гарын бол SQL-гүй
        used_calc = {i.calc or i.def_id for i in cat.indicators.values()}
        for cid, calc in sorted(cat.calcs.items()):
            errors.extend(calc.errors)
            if calc.mode == "sql" and not calc.sql_from:
                if conns and calc.connection and calc.connection not in conns:
                    errors.append(f"{cid}: connection '{calc.connection}' config/*.yaml-д алга")
                e, w = check_sql(calc, conns.get(calc.connection))
                errors.extend(e)
                warnings.extend(w)
            if cid not in used_calc:
                warnings.append(f"{cid}: ямар ч үзүүлэлт ашиглаагүй (activity.yaml shared: эсвэл calc: {cid})")

        e, w = check_shared()
        errors += e
        warnings += w
        # Давхардал: ижил SQL-тэй хоёр файл → sql_from эсвэл calc: SH_NNN / shared/ ашиглана
        seen: dict[str, str] = {}
        used: set[str] = set()
        for ind in sorted([*cat.indicators.values(), *cat.calcs.values()], key=lambda i: i.indicator_id):
            if ind.sql_from or ind.mode != "sql" or not ind.sql_path.exists():
                continue
            raw = ind.read_sql()
            used.update(shared_refs(raw))
            key = hashlib.sha1(_normalized(raw).encode()).hexdigest()
            if key in seen:
                warnings.append(f"{ind.indicator_id}: SQL нь {seen[key]}-тэй яг ижил — sql_from: {seen[key]} "
                                f"эсвэл calc: SH_NNN (нийтлэг тооцоолол) ашиглана")
            else:
                seen[key] = ind.indicator_id
        warnings += _unused_shared(used)

        # Үйл ажиллагаа: жингийн нийлбэр = 100, BRANCHID заавал, давхардахгүй
        seen_branch: dict[str, str] = {}
        for aid, act in sorted(cat.activities.items()):
            if act.example:
                continue
            inds = [i for i in cat.by_activity(aid) if i.enabled]
            total = sum(i.weight or 0 for i in inds)
            if inds and abs(total - 100) > 0.01:
                warnings.append(f"{aid}: жингийн нийлбэр {total:g}% (100 байх ёстой)")
            if not act.branch_id:          # тохиргооны (кодын биш) асуудал — run нь BRANCH_NOT_MAPPED-аар алгасна
                warnings.append(f"{aid}: BRANCHID алга (ТОДРУУЛАХ) — config/activity_map.csv эсвэл activity.yaml-д "
                                f"branch_id бичих хүртэл үр дүн хадгалагдахгүй")
            elif act.branch_id in seen_branch:
                errors.append(f"{aid}: BRANCHID {act.branch_id} нь {seen_branch[act.branch_id]}-тэй давхацсан")
            else:
                seen_branch[act.branch_id] = aid

    ts = TopologicalSorter()
    for ind in [*cat.indicators.values(), *cat.calcs.values()]:
        ts.add(ind.indicator_id, *[d for d in ind.dependencies if cat.get(d) is not None])
    try:
        ts.prepare()
    except CycleError as exc:
        errors.append(f"Dependency тойрог үүссэн: {' -> '.join(exc.args[1])}")
    return errors, warnings
