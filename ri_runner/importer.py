"""Master жагсаалт (15 багана) → activities/ бүтэц.

    python ri.py import master.xlsx --dry-run      # юу үүсэхийг харах
    python ri.py import master.xlsx                # файлуудыг үүсгэх (байгаа файлд хүрэхгүй)
    python ri.py import master.xlsx --update       # + байгаа файлын master хэсгийг (нэр, жин, шатлал, хугацаа …)
                                                   #   засагдсан master-аар шинэчилнэ — SQL, тохиргоонд хүрэхгүй

Мөр бүр → activities/act_GG_slug/ri_GG_NNNN.sql (Бүлэг GG, master-ийн № NNNN):
  - Автоматжуулах = "Үгүй"/хоосон                  → manual: true   (ri.py manual-аар оруулна)
  - Автоматжуулах = "Тийм", нэр нь ≥ --shared-min  → calc: SH_NNN   (activities/_shared/sh_NNN.sql, 1 SQL)
    үйл ажиллагаанд давтагдсан
  - Автоматжуулах = "Тийм", бусад                  → өөрийн SQL (TODO загвар)
Master-ийн жин, шатлал, оноо, мэдээллийн суваг, аргачлал тохиргоонд хуулагдана.
Шатлал задарсан эсэхийн тайлан: output/import_report.csv
"""
import csv
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from .config import ACTIVITIES_DIR, OUTPUT_DIR, TEMPLATES_DIR
from .metadata import SHARED_DIR, infer_period, load_catalog, split_front_matter
from .scale import parse_scale_text

COLUMNS = {   # түлхүүр: толгойн нэрэнд агуулагдах текст (жижиг үсгээр)
    "group": ("бүлэг",), "number": ("№",), "activity_old": ("хуучин",), "activity": ("үйл ажиллагаа",),
    "indicator": ("risk indicator", "үзүүлэлт"), "weight": ("жин",), "source_system": ("суваг",),
    "required_info": ("шаардлагатай",), "method": ("аргачлал",), "period_text": ("хамрах",),
    "score_type": ("score",), "scale": ("scale", "шатлал"), "automatable": ("автоматжуулах",),
    "data_mapping": ("data mapping",), "development": ("хөгжүүлэлт",),
}
ORDER = ("group", "number", "activity", "activity_old", "indicator", "weight", "source_system",
         "required_info", "method", "period_text", "score_type", "scale", "automatable", "data_mapping",
         "development")


def read_table(path: Path, sheet: str | None = None) -> list[list]:
    """xlsx (жинхэнэ) эсвэл csv/tsv (.xlsx өргөтгөлтэй ч байж болно)."""
    if zipfile.is_zipfile(path):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        return [["" if v is None else v for v in r] for r in ws.iter_rows(values_only=True)]
    text = path.read_text(encoding="utf-8-sig")
    delim = "\t" if text.split("\n", 1)[0].count("\t") >= 3 else ","
    return [r for r in csv.reader(text.splitlines(keepends=True), delimiter=delim)]


def find_columns(header: list) -> dict:
    h = [str(x or "").strip().lower() for x in header]
    found = {}
    for key in ("activity_old", "required_info", "automatable", "data_mapping", "development", "group",
                "number", "indicator", "weight", "source_system", "method", "period_text", "scale",
                "score_type", "activity"):
        for i, name in enumerate(h):
            if i in found.values():
                continue
            if key == "score_type" and name != "score":
                continue
            if key == "scale" and name not in ("scale", "шатлал"):
                continue
            if any(t in name for t in COLUMNS[key]):
                found[key] = i
                break
    for pos, key in enumerate(ORDER):                     # толгой таниагүй бол байрлалаар
        if key not in found and pos < len(h) and pos not in found.values():
            found[key] = pos
    return found


def norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower().rstrip(".")


_TRANSLIT = dict(zip("абвгдеёжзийклмноөпрстуүфхцчшщъыьэюя",
                     ["a", "b", "v", "g", "d", "e", "yo", "j", "z", "i", "i", "k", "l", "m", "n", "o", "o",
                      "p", "r", "s", "t", "u", "u", "f", "kh", "ts", "ch", "sh", "sh", "", "y", "", "e", "yu", "ya"]))


def slugify(text: str, words: int = 3) -> str:
    latin = "".join(_TRANSLIT.get(ch, ch) for ch in str(text).lower())
    parts = [p for p in re.split(r"[^a-z0-9]+", latin) if p][:words]
    return "_".join(parts)[:40] or "activity"


def _q(v) -> str:
    """YAML-д аюулгүй утга (JSON string нь YAML-ийн хүчинтэй double-quoted)."""
    return json.dumps(str(v), ensure_ascii=False)


def _block(key: str, text: str) -> str:
    lines = [ln.rstrip() for ln in str(text).replace("\r", "").split("\n") if ln.strip()]
    if not lines:
        return ""
    if len(lines) == 1:
        return f"{key}: {_q(lines[0])}\n"
    return f"{key}: |\n" + "".join(f"  {ln.strip()}\n" for ln in lines)


def _master_fields(r: dict) -> str:
    out = ""
    if r["weight"] is not None:
        out += f"weight: {r['weight']:g}                       # үйл ажиллагаа доторх жин (%)\n"
    for key in ("score_type",):
        if r[key]:
            out += f"{key}: {_q(r[key])}\n"
    out += _block("scale_text", r["scale"])
    for key in ("source_system", "required_info", "method", "period_text", "automatable"):
        out += _block(key, r[key])
    if r["data_mapping"]:
        out += _block("data_mapping", r["data_mapping"])
    return out


MASTER_BLOCK_RE = re.compile(r"^# ── Master[^\n]*\n(?:(?!# ──|---\*/|# test_dates).*\n)*", re.M)
_PERIOD_LINE = "                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)\n"


def master_block(r: dict) -> str:
    return "# ── Master ──\n" + _master_fields(r) + f"period: {infer_period(r['period_text'])}" + _PERIOD_LINE


def _yaml_head(head: str) -> dict:
    import yaml
    try:
        d = yaml.safe_load(head.split("/*---", 1)[-1]) or {}
    except yaml.YAMLError:
        return {}
    return d if isinstance(d, dict) else {}


def _norm_val(v):
    if isinstance(v, str):
        return "\n".join(ln.strip() for ln in v.strip().splitlines() if ln.strip())
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def update_master(path: Path, r: dict) -> tuple[str | None, list[str]]:
    """Байгаа файлын name_mn ба master хэсгийг шинэчилсэн текст (өөрчлөлтгүй бол None), өөрчлөгдсөн талбарууд."""
    text = path.read_text(encoding="utf-8")
    head, sep, body = text.partition("---*/")
    m = MASTER_BLOCK_RE.search(head)
    if not sep or not m:
        return None, ["# ── Master ── хэсэг олдсонгүй — гараар"]
    old_block = m.group(0)
    explicit_period = re.search(r"^period:", head[:m.start()] + head[m.end():], re.M)
    new_block = master_block(r)
    if explicit_period or re.search(r"^period:", old_block, re.M) is None and "period:" in head:
        new_block = re.sub(r"^period: .*\n", "", new_block, flags=re.M)     # гараар бичсэн period хэвээр
    new_head = head[:m.start()] + new_block + head[m.end():]
    new_head = re.sub(r"^name_mn: .*$", lambda _: f"name_mn: {_q(r['indicator'])}", new_head, count=1, flags=re.M)
    old_meta, new_meta = _yaml_head(head), _yaml_head(new_head)
    old_meta.setdefault("period", infer_period(old_meta.get("period_text")))   # бичээгүй = master-аас
    changed = sorted(k for k in set(old_meta) | set(new_meta)
                     if _norm_val(old_meta.get(k)) != _norm_val(new_meta.get(k)))
    if not changed:
        return None, []
    return new_head + sep + body, changed


def _parse_weight(v):
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(v or ""))
    return float(m.group().replace(",", ".")) if m else None


def _sql_template(conn_type: str) -> str:
    name = "indicator_clickhouse.sql.tmpl" if conn_type == "clickhouse" else "indicator_oracle.sql.tmpl"
    text = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    return text.split("---*/", 1)[1].lstrip("\n")


def indicator_text(iid: str, r: dict, mode: str, calc: str | None) -> str:
    head = f"/*---\nindicator_id: {iid}\nname_mn: {_q(r['indicator'])}\n"
    if mode == "manual":
        head += "manual: true                    # хүн үнэлнэ: ri.py manual template / load\n"
    elif mode == "shared":
        head += f"calc: {calc}                     # нийтлэг тооцоолол: activities/_shared/{calc.lower()}.sql\n"
    head += "status: TODO\nversion: 0.1.0\n# ── Master ──\n" + _master_fields(r)
    head += (f"period: {infer_period(r['period_text'])}"
             "                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)\n")
    if mode == "sql":
        head += "# test_dates: [2026-06-30, 2026-09-30]\n"
    head += "---*/\n"
    return head + (_sql_template("oracle") if mode == "sql" else "")


def calc_text(cid: str, name: str, users: list[str], connection: str, frequency: str) -> str:
    body = _sql_template("oracle")
    return (f"/*---\nindicator_id: {cid}\nname_mn: {_q(name)}\n"
            f"description: >\n  Нийтлэг тооцоолол — SOL бүрийн мөр (ENTITY_LEVEL='SOL'). Үйл ажиллагаа бүр өөрийн\n"
            f"  SOL-уудаар нэгтгэнэ. Ашигладаг: {', '.join(users[:12])}{' …' if len(users) > 12 else ''}\n"
            f"connection: {connection}\nfrequency: {frequency}\nstatus: TODO\nversion: 0.1.0\n---*/\n" + body)


def read_master(path: Path, sheet: str | None = None) -> tuple[list[dict], list[str]]:
    """master (xlsx / tsv) → мөрүүд {g, n, iid, indicator, weight, scale, …}, алдаанууд."""
    table = read_table(path, sheet)
    hi = next((i for i, r in enumerate(table[:20]) if any(str(x).strip().lower() == "бүлэг" for x in r)), 0)
    cols = find_columns(table[hi])
    errors, rows, seen = [], [], set()
    for line_no, raw in enumerate(table[hi + 1:], start=hi + 2):
        if not raw or all(str(v).strip() == "" for v in raw):
            continue
        r = {k: (str(raw[i]).strip() if i < len(raw) and raw[i] is not None else "") for k, i in cols.items()}
        try:
            g, n = int(float(r["group"])), int(float(r["number"]))
        except (TypeError, ValueError):
            errors.append(f"мөр {line_no}: Бүлэг/№ тоо биш ({r.get('group')}, {r.get('number')})")
            continue
        if not r.get("indicator"):
            errors.append(f"мөр {line_no}: үзүүлэлтийн нэр хоосон")
            continue
        if not (1 <= g <= 99 and 1 <= n <= 8999):
            errors.append(f"мөр {line_no}: Бүлэг 1–99, № 1–8999 ({g}, {n})")
            continue
        iid = f"RI_{g:02d}_{n:04d}"
        if iid in seen:
            errors.append(f"мөр {line_no}: {iid} давхардсан")
            continue
        seen.add(iid)
        r.update(g=g, n=n, iid=iid, line=line_no, weight=_parse_weight(r.get("weight")))
        for k in ORDER:
            r.setdefault(k, "")
        rows.append(r)
    return rows, errors


# ── Нийтлэг тодорхойлолт (activities/_shared/sh_NNN.sql) ───────────────────────
_ID_KEYS = ("indicator_id", "name_mn", "status", "version", "calc", "manual", "weight", "score_type", "scale_text",
            "source_system", "required_info", "method", "period_text", "automatable", "data_mapping", "period")


def def_master_block(f: dict, n_acts: int) -> str:
    out = f"# ── Master ── (нийтлэг: {n_acts} үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)\n"
    if f["score_type"]:
        out += f"score_type: {_q(f['score_type'])}\n"
    out += _block("scale_text", f["scale"])
    for key in ("source_system", "required_info", "method", "period_text", "automatable", "data_mapping"):
        out += _block(key, f[key])
    return out + f"period: {infer_period(f['period_text'])}" + _PERIOD_LINE


def def_text(def_id: str, d, code: dict | None) -> str:
    """Шинэ нийтлэг тодорхойлолт. code = {"tech": тохиргооны мөрүүд, "body": SQL, "status", "version"} эсвэл None."""
    head = f"/*---\nindicator_id: {def_id}\nname_mn: {_q(d.name)}\n"
    if code is None:
        auto = d.fields["automatable"].strip().lower().startswith("тийм")
        head += ("manual: true                    # хүн үнэлнэ (ri.py manual). SQL бичвэл бүх үйл ажиллагаанд автомат: "
                 "manual-ийг хасаад доор нь SQL\n")
        if auto:
            head += "# master: Автоматжуулах = Тийм — SQL бичих хүртэл гараар\n"
        head += "status: TODO\nversion: 0.1.0\n"
    else:
        head += f"status: {code['status']}\nversion: {code['version']}\n"
    head += def_master_block(d.fields, len(d.groups))
    if code is not None:
        head += "# ── Тооцоолол ──\n" + code["tech"]
    return head + "---*/\n" + (code["body"] if code else "")


def strip_keys(meta: str, keys=_ID_KEYS) -> str:
    """Front matter-аас master / ID талбаруудыг (үргэлжлэл мөртэй нь) хасна, бусдыг (comment-той) хэвээр."""
    out, skip = [], False
    for ln in meta.split("\n"):
        m = re.match(r"^([a-z_]+):", ln)
        if m:
            skip = m.group(1) in keys
        elif ln.startswith("# ── Master") or ln.startswith("# ── Тооцоолол"):
            skip = False
            continue
        elif not (ln.startswith(" ") or ln == ""):
            skip = False
        if not skip:
            out.append(ln)
    return "\n".join(x for x in out).strip("\n") + "\n"


def instance_code(path: Path, defaults: dict | None = None) -> dict | None:
    """Хуулбар файлд өөрийн SQL (template биш) эсвэл sql_from байвал түүнийг тодорхойлолт руу зөөх мэдээлэл.
    connection, frequency-г үйл ажиллагааны defaults-аас өвлөж байсан бол тодорхойлолтод шууд бичнэ."""
    import yaml
    meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    if meta is None:
        return None
    d = yaml.safe_load(meta) or {}
    real = body.strip() and "TODO_TABLE" not in body
    if not real and not d.get("sql_from"):
        return None
    tech = strip_keys(meta)
    for key in ("connection", "frequency"):
        if key not in d and (defaults or {}).get(key):
            tech = f"{key}: {defaults[key]}\n" + tech
    return {"tech": tech, "body": body if real else "", "status": d.get("status", "TODO"),
            "version": d.get("version", "0.1.0"), "sql_from": d.get("sql_from")}


def update_def_master(path: Path, d) -> tuple[str | None, list[str]]:
    """Байгаа тодорхойлолтын master хэсгийг шинэчилнэ (байхгүй бол version-ий дараа нэмнэ)."""
    text = path.read_text(encoding="utf-8")
    head, sep, body = text.partition("---*/")
    block = def_master_block(d.fields, len(d.groups))
    m = MASTER_BLOCK_RE.search(head)
    if m:
        new_head = head[:m.start()] + block + head[m.end():]
    else:
        v = re.search(r"^version: .*\n", head, re.M)
        at = v.end() if v else len(head)
        new_head = head[:at] + block + ("# ── Тооцоолол ──\n" if "# ── Тооцоолол" not in head else "") + head[at:]
    old_meta, new_meta = _yaml_head(head), _yaml_head(new_head)
    old_meta.setdefault("period", new_meta.get("period"))
    changed = sorted(k for k in set(old_meta) | set(new_meta) if _norm_val(old_meta.get(k)) != _norm_val(new_meta.get(k)))
    return (new_head + sep + body if changed else None), changed


# ── activity.yaml shared: ─────────────────────────────────────────────────────
MANIFEST_MARK = "# ── Нийтлэг үзүүлэлт"
_KEEP_KEYS = ("params", "enabled", "note", "period", "scale")      # гараар нэмсэн — import дарахгүй


def manifest_block(entries: list[dict], names: dict) -> str:
    out = (f"\n{MANIFEST_MARK} (ri.py import үүсгэнэ — id, def, weight, зөрүү нь master-аас; params, enabled, note-ийг "
           "гараар нэмж болно) ──\n"
           "# Олон үйл ажиллагаанд давтагддаг үзүүлэлт: тодорхойлолт activities/_shared/sh_NNN.sql, энд №, жин, зөрүү.\n"
           "shared:\n")
    for e in sorted(entries, key=lambda e: e["id"]):
        simple = {k: e[k] for k in ("id", "def", "weight") if k in e}
        rest = {k: v for k, v in e.items() if k not in simple}
        w = "null" if simple.get("weight") is None else f"{simple['weight']:g}"
        line = f"  - {{id: {simple['id']}, def: {simple['def']}, weight: {w}}}"
        if not rest:
            out += f"{line:<56} # {names.get(e['def'], '')[:60]}\n"
            continue
        out += f"  - id: {simple['id']}                              # {names.get(e['def'], '')[:60]}\n"
        out += f"    def: {simple['def']}\n    weight: {w}\n"
        for k, v in rest.items():
            if isinstance(v, str) and "\n" in v.strip():
                out += f"    {k}: |\n" + "".join(f"      {ln.strip()}\n" for ln in v.strip().splitlines() if ln.strip())
            elif isinstance(v, (dict, list, bool, int, float)):
                out += f"    {k}: {json.dumps(v, ensure_ascii=False)}\n"
            else:
                out += f"    {k}: {_q(v)}\n"
    return out


def write_manifest(path: Path, entries: list[dict], names: dict) -> bool:
    import yaml
    text = path.read_text(encoding="utf-8")
    old = (yaml.safe_load(text) or {}).get("shared") or []
    keep = {str(e["id"]): {k: e[k] for k in _KEEP_KEYS if k in e} for e in old if isinstance(e, dict) and "id" in e}
    entries = [{**e, **keep.get(e["id"], {})} for e in entries]
    base = text.split(f"\n{MANIFEST_MARK}", 1)[0].rstrip("\n") + "\n"
    new = base + (manifest_block(entries, names) if entries else "")
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def import_master(path: str, sheet: str | None = None, owner: str = "unassigned_owner",
                  reviewer: str = "unassigned_reviewer", connection: str = "oracle_whouse",
                  frequency: str = "quarterly", shared_min: int = 2, dry_run: bool = False, groups=None,
                  root: Path = ACTIVITIES_DIR, update: bool = False) -> int:
    """Master → activities/ (давхардалгүй бүтэц: ri_runner/dedup.py-ийн дүрмээр).

    update=False: байхгүй файл / мөрийг л үүсгэнэ. update=True: + master хэсгийг шинэчилнэ, нийтлэг нэрийн хуучин
    хуулбар файлыг (ri_GG_NNNN.sql, calc: эсвэл manual) activity.yaml shared: мөр болгож устгана — SQL-тэй бол
    тодорхойлолт руу зөөнө."""
    from . import dedup
    from .orgmap import group_names_en
    src = Path(path)
    if not src.exists():
        print(f"Файл олдсонгүй: {src}")
        return 2
    rows, errors = read_master(src, sheet)
    defs = dedup.decide(rows)
    cat = load_catalog(root)
    pfx = "[DRY-RUN] " if dry_run else ""

    # Тодорхойлолтын ID: байгаа SH_NNN-ийг нэрээр нь, шинийг дараалсан дугаараар
    existing = {dedup.norm_key(c.name_mn): cid for cid, c in cat.calcs.items()}
    next_no = max([int(c[3:]) for c in cat.calcs] or [0]) + 1
    for d in defs:
        if len(d.groups) >= shared_min:
            d.def_id = existing.get(d.key) or f"SH_{next_no:03d}"
            if d.key not in existing:
                next_no += 1
    selected = set(groups or [])
    names_en = group_names_en()
    folder_of = {a.group_no: a.folder for a in cat.activities.values()}
    new_acts, writes, deletes, manifests, notes = [], {}, [], defaultdict(list), []
    report = []

    for r in rows:
        if selected and r["g"] not in selected:
            continue
        if r["g"] not in folder_of:
            slug = slugify(names_en.get(r["g"]) or r["activity"] or f"group {r['g']}", words=4)
            folder_of[r["g"]] = root / f"act_{r['g']:02d}_{slug}"
            new_acts.append((folder_of[r["g"]], r))

    id_map = {}                                            # хуучин хуулбар ID → тодорхойлолт (sql_from-д)
    for d in defs:
        rs = [r for r in d.rows if not selected or r["g"] in selected]
        if not rs:
            continue
        if d.def_id:                                       # ── нийтлэг ──
            def_path = root / SHARED_DIR / f"{d.def_id.lower()}.sql"
            code, conflicts = None, []
            for r in sorted(d.rows, key=lambda r: r["n"]):
                f = folder_of.get(r["g"], Path("/nonexistent")) / f"{r['iid'].lower()}.sql"
                if f.exists() and update:
                    act = next((a for a in cat.activities.values() if a.group_no == r["g"]), None)
                    c = instance_code(f, act.defaults if act else None)
                    if c and code is None:
                        code = c
                    elif c and c["body"].strip() != code["body"].strip():
                        conflicts.append(r["iid"])
            if not def_path.exists():
                writes[def_path] = def_text(d.def_id, d, code)
            elif update:
                txt, changed = update_def_master(def_path, d)
                if txt:
                    writes[def_path] = txt
                if code and d.def_id in cat.calcs and cat.calcs[d.def_id].mode == "manual":
                    notes.append(f"{d.def_id}: гарын тодорхойлолт, хуулбарт SQL байна ({code['status']}) — гараар шилжүүлнэ")
            for r in rs:
                dec = d.decisions[r["iid"]]
                f = folder_of[r["g"]] / f"{r['iid'].lower()}.sql"
                if r["iid"] in conflicts:
                    notes.append(f"{r['iid']}: {d.def_id}-ээс өөр SQL-тэй — тусдаа файл хэвээр")
                    report.append(_rep(r, d, "өөрийн файл (өөр SQL)", dec))
                    continue
                if f.exists() and not update:
                    report.append(_rep(r, d, "хуучин файл (--update хийвэл shared:)", dec))
                    continue
                if f.exists():
                    deletes.append(f)
                id_map[r["iid"]] = d.def_id
                manifests[r["g"]].append({"id": r["iid"], "def": d.def_id, "weight": r["weight"], **dec.overrides})
                report.append(_rep(r, d, f"shared: {d.def_id}", dec))
        else:                                              # ── ганц үйл ажиллагаа ──
            r = rs[0]
            f = folder_of[r["g"]] / f"{r['iid'].lower()}.sql"
            mode = "sql" if dedup._auto(r["automatable"]) else "manual"
            if f.exists() or r["iid"] in cat.indicators:
                if update and f.exists():
                    txt, _ = update_master(f, r)
                    if txt:
                        writes[f] = txt
                report.append(_rep(r, d, "өөрийн файл", d.decisions[r["iid"]]))
                continue
            writes[f] = indicator_text(r["iid"], r, mode, None)
            report.append(_rep(r, d, "өөрийн файл (шинэ)", d.decisions[r["iid"]]))

    # sql_from: хуучин хуулбар ID → тодорхойлолт (тодорхойлолт болон ганц файлуудад)
    if id_map and update:
        for f in [*root.glob("act_*/ri_*.sql"), *(root / SHARED_DIR).glob("sh_*.sql"), *writes]:
            if f in deletes:
                continue
            txt = writes.get(f) or (f.read_text(encoding="utf-8") if f.exists() else "")
            new_txt = re.sub(r"^(sql_from:\s*)(RI_\d{2}_\d{4})", lambda m: m.group(1) + id_map.get(m.group(2), m.group(2)),
                             txt, flags=re.M)
            if new_txt != txt:
                writes[f] = new_txt

    # Тайлан
    n_common = sum(1 for d in defs if d.def_id)
    n_rows_common = sum(len(d.rows) for d in defs if d.def_id)
    print(f"{pfx}Master: {len(rows)} мөр, {len({r['g'] for r in rows})} үйл ажиллагаа → {len(defs)} тодорхойлолт "
          f"(давхардал {len(rows) - len(defs)} хасагдав)")
    print(f"  нийтлэг (2+ үйл ажиллагаа) {n_common:>4}  → {n_rows_common} мөр activity.yaml shared:-д")
    print(f"  ганц үйл ажиллагааны       {len(defs) - n_common:>4}  → өөрийн файл")
    overrides = sum(1 for d in defs for dec in d.decisions.values() if dec.overrides)
    fixed = sum(1 for d in defs for dec in d.decisions.values() if any("→ нийтлэг шатлал" in n for n in dec.notes))
    print(f"  зөрүүтэй мөр: дарсан {overrides}, эвдэрсэн шатлалыг нийтлэгээр {fixed} (python ri.py dedup — дэлгэрэнгүй)")
    print(f"\n{pfx}Үйл ажиллагаа +{len(new_acts)}, бичих файл {len(writes)}, устгах хуулбар {len(deletes)}, "
          f"shared: мөр {sum(len(v) for v in manifests.values())}")
    for e in errors[:50]:
        print(f"  ✘ {e}")
    for n in notes[:30]:
        print(f"  ! {n}")
    OUTPUT_DIR.mkdir(exist_ok=True)
    rep = OUTPUT_DIR / "import_report.csv"
    with rep.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(report[0]) if report else ["indicator_id"])
        w.writeheader()
        w.writerows(report)
    print(f"Тайлан: {rep}")
    if dry_run:
        return 1 if errors else 0

    for folder, r in new_acts:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "activity.yaml").write_text(
            f"activity_id: ACT_{r['g']:02d}\nactivity_name_mn: {_q(r['activity'])}\n"
            + (f"activity_name_mn_old: {_q(r['activity_old'])}\n" if r["activity_old"] else "")
            + f"activity_name_en: {_q(names_en.get(r['g'], ''))}\n"
            f"# branch_id: \"\"          # BRANCHID — өгөөгүй бол config/activity_map.csv-ээс (бүлгийн дугаараар)\n"
            f"owner: {owner}\nreviewer: {reviewer}\n\ndefaults:\n  connection: {connection}\n"
            f"  frequency: {frequency}\n  timeout_seconds: 600\n", encoding="utf-8")
    for f, txt in writes.items():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt, encoding="utf-8")
    for f in deletes:
        f.unlink()
    names = {d.def_id: d.name for d in defs if d.def_id}
    for g, entries in manifests.items():
        write_manifest(folder_of[g] / "activity.yaml", entries, names)
    after = load_catalog(root)
    n_err = len(after.errors) + sum(len(i.errors) for i in after.indicators.values())
    print(f"Дууслаа. Catalog: {len(after.activities)} үйл ажиллагаа, {len(after.indicators)} үзүүлэлт, "
          f"{len(after.calcs)} нийтлэг тодорхойлолт, metadata алдаа {n_err}")
    if new_acts:
        print("Санамж: .gitlab/CODEOWNERS-д шинэ үйл ажиллагааны owner/reviewer-ийг нэмнэ үү.")
    return 1 if errors else 0


def _rep(r: dict, d, where: str, dec) -> dict:
    return {"indicator_id": r["iid"], "group": r["g"], "name": r["indicator"], "definition": d.def_id or r["iid"],
            "n_activities": len(d.groups), "placement": where, "overrides": ", ".join(dec.overrides),
            "notes": "; ".join(dec.notes), "weight": r["weight"], "scale_text": r["scale"]}
