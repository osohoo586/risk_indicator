"""Master-ийн давхардлыг шийдэх дүрэм — import болон `ri.py dedup` тайлан хоёулаа энийг ашиглана.

Шийдвэр:
  1. Нэр нормчлох (жижиг үсэг, ё→е, хашилт, зай, цэг таслал) → ижил нэр = НЭГ тодорхойлолт.
  2. 2+ үйл ажиллагаанд байгаа нэр → нийтлэг тодорхойлолт (activities/_shared/sh_NNN.sql), үйл ажиллагаа бүрт
     зөвхөн №, жин (activity.yaml shared:). Ганц үйл ажиллагаанд → өөрийн файл (ri_GG_NNNN.sql).
  3. Талбар бүрийн нийтлэг утга = хамгийн түгээмэл хоосон бус утга. Шатлал бол ЗӨВХӨН задардаг (parser) хуулбаруудаас.
  4. Үйл ажиллагааны утга нийтлэгээс өөр бол:
       шатлал задрахгүй (мастерийн эвдрэл: "s-Дунд", шилжсэн багана)  → нийтлэг шатлал (засах шаардлагагүй)
       шатлал = нийтлэг + илүү мөр                                    → нийтлэг шатлал (илүү мөрийг хасав)
       шатлал задардаг, өөр (санаатай хувилбар)                       → тухайн үйл ажиллагаанд дарна
       хамрах хугацаа хоосон                                          → нийтлэгийнх
       хамрах хугацаа өөр                                             → тухайн үйл ажиллагаанд дарна
       бүлэг (score), аргачлал өөр                                     → тухайн үйл ажиллагаанд дарна
       автоматжуулах зөрүүтэй (Тийм / Үгүй)                           → тодорхойлолтод SQL байвал бүгд автомат
  5. Нэрийн төгсгөлөөрөө л ялгаатай (…-УБ / …-ОН, дебит / кредит) "гэр бүл" — тусдаа үзүүлэлт хэвээр (утга нь
     өөр), гэхдээ SQL-ийг НЭГ удаа бичээд `sql_from` + `params`-аар дахин ашиглах боломж. Төстэй нэр (≥ 0.9) —
     хүн шалгах жагсаалт (автоматаар нэгтгэхгүй).
"""
import difflib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .metadata import infer_period
from .scale import parse_scale_text

MASTER_FIELDS = ("score_type", "scale", "source_system", "required_info", "method", "period_text", "automatable",
                 "data_mapping")


def norm_key(name: str) -> str:
    """Давхардлын түлхүүр: 'Action plan биелэлт.' == 'action plan  биелэлт'."""
    s = str(name or "").lower().replace("ё", "е")
    s = re.sub(r"[“”\"'«»]", "", s)
    s = re.sub(r"\s*([-/,.:;()])\s*", r"\1", s)
    return re.sub(r"\s+", " ", s).strip(" .,;:-")


def lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in str(text or "").replace("\r", "").split("\n") if ln.strip()]


def scale_key(text: str) -> str:
    return " | ".join(lines(text))


def parses(text: str) -> bool:
    if not str(text or "").strip():
        return False
    scale, err = parse_scale_text(text)
    return scale is not None and not err


def medoid(values) -> str:
    """Бусадтайгаа хамгийн төстэй текст (аргачлал г.м. үйл ажиллагаа бүр бага зэрэг өөр бичсэн талбарт)."""
    vals = [v for v in values if str(v or "").strip()]
    uniq = list(dict.fromkeys(vals))
    if len(uniq) <= 2:
        return common(vals)
    def score(a):
        return sum(difflib.SequenceMatcher(None, norm_key(a), norm_key(b)).ratio() for b in vals)
    return max(uniq, key=score)


def common(values) -> str:
    """Хамгийн түгээмэл хоосон бус утга (тэнцвэл эхэнд гарсан)."""
    vals = [v for v in values if str(v or "").strip()]
    if not vals:
        return ""
    counts = Counter(vals)
    best = max(counts.values())
    return next(v for v in vals if counts[v] == best)


@dataclass
class Decision:
    """Нэг master мөрийн шийдвэр."""
    iid: str
    group: int
    def_key: str
    overrides: dict = field(default_factory=dict)     # activity.yaml-д дарах талбар
    notes: list = field(default_factory=list)         # тайлбар: "шатлал эвдэрсэн → нийтлэг" г.м.


@dataclass
class Definition:
    key: str
    name: str
    rows: list                                        # master мөрүүд
    fields: dict                                      # нийтлэг утга (MASTER_FIELDS)
    decisions: dict                                   # iid → Decision
    def_id: str = ""

    @property
    def groups(self) -> list[int]:
        return sorted({r["g"] for r in self.rows})

    @property
    def is_common(self) -> bool:
        return len(self.groups) >= 2


def decide(rows: list[dict]) -> list[Definition]:
    """master мөрүүд (importer.read_master) → тодорхойлолтууд + мөр бүрийн шийдвэр."""
    by_key: dict[str, list] = defaultdict(list)
    for r in rows:
        by_key[norm_key(r["indicator"])].append(r)
    out = []
    for key, rs in by_key.items():
        f = {k: (medoid if k in ("method", "required_info", "source_system") else common)(r[k] for r in rs)
             for k in MASTER_FIELDS}
        good = [r["scale"] for r in rs if parses(r["scale"])]
        f["scale"] = (max(Counter(scale_key(s) for s in good).items(), key=lambda kv: kv[1])[0] if good else
                      scale_key(common(r["scale"] for r in rs)))
        f["scale"] = next((r["scale"] for r in rs if scale_key(r["scale"]) == f["scale"]), f["scale"])
        name = common(r["indicator"] for r in rs)
        d = Definition(key, name, rs, f, {})
        for r in rs:
            dec = Decision(r["iid"], r["g"], key)
            if len({x["g"] for x in rs}) >= 2:
                _compare(r, f, dec)
            d.decisions[r["iid"]] = dec
        out.append(d)
    return sorted(out, key=lambda d: (-len(d.groups), min(r["n"] for r in d.rows)))


def _compare(r: dict, f: dict, dec: Decision) -> None:
    sk, canon = scale_key(r["scale"]), scale_key(f["scale"])
    if sk != canon:
        if not r["scale"].strip():
            dec.notes.append("шатлал хоосон → нийтлэг шатлал")
        elif not parses(r["scale"]):
            dec.notes.append("шатлал задрахгүй (master эвдэрсэн) → нийтлэг шатлал")
        elif set(lines(f["scale"])) == set(lines(r["scale"])):
            dec.notes.append("шатлалд давхардсан мөр → нийтлэг шатлал")
        elif set(lines(f["scale"])) < set(lines(r["scale"])):
            extra = [ln for ln in lines(r["scale"]) if ln not in set(lines(f["scale"]))]
            dec.notes.append(f"шатлалд илүү мөр {extra[:2]} → нийтлэг шатлал")
        else:
            dec.overrides["scale_text"] = r["scale"]
            dec.notes.append("өөр шатлал (санаатай хувилбар) → энэ үйл ажиллагаанд")
    if not r["period_text"].strip():
        if f["period_text"]:
            dec.notes.append("хамрах хугацаа хоосон → нийтлэгийнх")
    elif infer_period(r["period_text"]) != infer_period(f["period_text"]):
        dec.overrides["period_text"] = r["period_text"]
        dec.notes.append(f"хамрах хугацаа өөр ({infer_period(r['period_text'])}) → энэ үйл ажиллагаанд")
    for k in ("score_type", "method"):
        if r[k].strip() and norm_key(r[k]) != norm_key(f[k]):
            dec.overrides[k] = r[k]
            dec.notes.append(f"{k} өөр → энэ үйл ажиллагаанд")
    a, b = _auto(r["automatable"]), _auto(f["automatable"])
    if a != b:
        dec.notes.append(f"автоматжуулах: master «{r['automatable'] or 'хоосон'}», нийтлэг «{f['automatable'] or 'хоосон'}»"
                         " → тодорхойлолтод SQL байвал автомат")


def _auto(v: str) -> bool:
    return str(v or "").strip().lower().startswith("тийм")


# ── Гэр бүл, төстэй нэр ───────────────────────────────────────────────────────
_QUAL_RE = re.compile(r"^(.*?)(?:-\s*([^-]{1,25})|\s*/([^/]{1,25})/|\.\s*([^.]{1,25})|\s*\(([^()]{1,25})\))$")


def base_of(key: str) -> tuple[str, str]:
    """'нийт ритэйл харилцагчийн тоо-уб' → ('нийт ритэйл харилцагчийн тоо', 'уб')."""
    m = _QUAL_RE.match(key)
    if not m or len(m.group(1)) < 8:
        return key, ""
    qual = next(g for g in m.groups()[1:] if g)
    return m.group(1).strip(" -./"), qual.strip()


def families(defs: list[Definition]) -> list[tuple[str, list[Definition]]]:
    """Нэрийн суурь ижил, төгсгөлөөрөө ялгаатай 2+ тодорхойлолт (жнь …-УБ, …-ОН)."""
    by_base: dict[str, list] = defaultdict(list)
    for d in defs:
        base, qual = base_of(d.key)
        if qual:
            by_base[base].append(d)
    return sorted(((b, ds) for b, ds in by_base.items() if len(ds) >= 2), key=lambda x: (-len(x[1]), x[0]))


def near_duplicates(defs: list[Definition], threshold: float = 0.9) -> list[tuple[float, Definition, Definition]]:
    """Гэр бүлд ороогүй төстэй нэрс — хүн шалгах."""
    fam = {d.key for _, ds in families(defs) for d in ds}
    keys = [d for d in defs if d.key not in fam]
    out = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            r = difflib.SequenceMatcher(None, a.key, b.key).ratio()
            if r >= threshold:
                out.append((round(r, 3), a, b))
    return sorted(out, key=lambda x: -x[0])


# ── Тайлан ────────────────────────────────────────────────────────────────────
NOTE_KINDS = (("задрахгүй", "эвдэрсэн шатлал → нийтлэг"), ("илүү мөр", "илүү мөр → нийтлэг"),
              ("давхардсан мөр", "давхардсан мөр → нийтлэг"),
              ("санаатай", "өөр шатлал (дарсан)"), ("хугацаа хоосон", "хугацаа хоосон → нийтлэг"),
              ("хугацаа өөр", "хугацаа өөр (дарсан)"), ("method", "аргачлал өөр (дарсан)"),
              ("score_type", "бүлэг өөр (дарсан)"), ("автоматжуулах", "автоматжуулах зөрүүтэй"),
              ("шатлал хоосон", "шатлал хоосон → нийтлэг"))


def _w(v) -> str:
    return "" if v is None else f"{v:g}"


def note_kind(note: str) -> str:
    return next((label for key, label in NOTE_KINDS if key in note), note)


def report_html(rows: list[dict], defs: list[Definition], cat) -> str:
    import html
    from collections import Counter
    e = html.escape
    by_key = {norm_key(c.name_mn): c for c in cat.calcs.values()}
    acts = {a.group_no: a for a in cat.activities.values()}
    common = [d for d in defs if d.is_common]
    single = [d for d in defs if not d.is_common]
    sql_defs = [d for d in common if by_key.get(d.key) is not None and by_key[d.key].mode == "sql"]
    auto_rows = sum(len(d.rows) for d in sql_defs)
    kinds = Counter(note_kind(n) for d in common for dec in d.decisions.values() for n in dec.notes)
    fam = families(defs)
    near = near_duplicates(defs)

    def badge(label, n, cls=""):
        return f"<span class='b {cls}'>{e(label)} {n}</span>" if n else ""

    rows_html = []
    for d in common:
        c = by_key.get(d.key)
        did = c.indicator_id if c else "—"
        mode = ("SQL" if c is not None and c.mode == "sql" else "гарын") + (f" · {c.status}" if c else "")
        kc = Counter(note_kind(n) for dec in d.decisions.values() for n in dec.notes)
        badges = "".join(badge(k, v, "warn" if "→ нийтлэг" in k else "") for k, v in kc.most_common())
        det = "".join(
            f"<tr><td>{r['g']}</td><td>{e(acts[r['g']].name_mn[:38] if r['g'] in acts else '')}</td><td>{r['iid']}</td>"
            f"<td class='num'>{_w(r['weight'])}</td>"
            f"<td class='w'>{e('; '.join(d.decisions[r['iid']].notes) or 'нийтлэгтэй ижил')}</td></tr>"
            for r in sorted(d.rows, key=lambda r: r["g"]))
        rows_html.append(
            f"<details><summary><code>{did}</code> <b>{e(d.name)}</b> <span class='mute'>· {len(d.groups)} үйл ажиллагаа · "
            f"{mode}</span> {badges}</summary>"
            f"<p class='mute'>Нийтлэг шатлал: <code>{e(scale_key(d.fields['scale'])[:220])}</code> · хугацаа: "
            f"{e(d.fields['period_text'] or '—')} → <code>{infer_period(d.fields['period_text'])}</code></p>"
            f"<div class='wrap'><table><tr><th>бүлэг</th><th>үйл ажиллагаа</th><th>үзүүлэлт</th><th>жин</th>"
            f"<th>шийдвэр</th></tr>{det}</table></div></details>")
    fam_html = "".join(
        f"<tr><td class='w'>{e(b)}</td><td class='w'>{e(', '.join(base_of(d.key)[1] for d in ds))}</td>"
        f"<td>{', '.join(str(g) for g in sorted({g for d in ds for g in d.groups}))}</td></tr>" for b, ds in fam)
    near_html = "".join(f"<tr><td class='num'>{r:.2f}</td><td class='w'>{e(a.name)}</td><td class='w'>{e(b.name)}</td></tr>"
                        for r, a, b in near)
    kinds_html = "".join(f"<tr><td>{e(k)}</td><td class='num'>{v}</td></tr>" for k, v in kinds.most_common())
    per_act = Counter(r["g"] for d in single for r in d.rows)
    per_act_c = Counter(r["g"] for d in common for r in d.rows)
    act_html = "".join(f"<tr><td>{g}</td><td>{e(acts[g].name_mn if g in acts else '')}</td><td class='num'>{per_act[g]}</td>"
                       f"<td class='num'>{per_act_c[g]}</td><td class='num'>{per_act[g] + per_act_c[g]}</td></tr>"
                       for g in sorted(set(per_act) | set(per_act_c)))
    return f"""<!doctype html><html lang="mn"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Үзүүлэлтийн давхардал</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=Onest:wght@600&display=swap">
<style>{CSS}</style></head><body><main>
<div class="eyebrow">ri.py dedup · master.xlsx → activities/</div>
<h1>Үзүүлэлтийн давхардлыг хэрхэн шийдсэн бэ</h1>
<p class="lead">master.xlsx-ийн {len(rows):,} мөр нь {len(defs)} давтагдашгүй үзүүлэлт. Олон үйл ажиллагаанд давтагддаг
{len(common)} үзүүлэлт (<b>{sum(len(d.rows) for d in common)}</b> мөр) нэг тодорхойлолт болж
(<code>activities/_shared/sh_NNN.sql</code>), үйл ажиллагаа бүрт зөвхөн №, жин (<code>activity.yaml shared:</code>)
үлдсэн. Ганц үйл ажиллагааны {len(single)} үзүүлэлт өөрийн файлтай.</p>
<div class="cards">
<div class="card"><b>{len(rows):,} → {len(defs)}</b><span>мөр → тодорхойлолт (давхардал {len(rows) - len(defs)} хасагдсан)</span></div>
<div class="card"><b>{len(common)}</b><span>нийтлэг тодорхойлолт · {sum(len(d.rows) for d in common)} мөр</span></div>
<div class="card"><b>{len(sql_defs)}</b><span>нийтлэг SQL · {auto_rows} үзүүлэлтийг автоматаар тооцно</span></div>
<div class="card"><b>{len(rows)} → {len(single) + len(common)}</b><span>файл (+ 35 activity.yaml)</span></div>
</div>
<h2>Шийдвэрийн дүрэм</h2>
<div class="wrap"><table>
<tr><td>Ижил нэр (жижиг үсэг, хашилт, зай, цэг таслал нормчилсон)</td><td class="w">НЭГ тодорхойлолт</td></tr>
<tr><td>Нийтлэг утга</td><td class="w">хамгийн түгээмэл; шатлал — зөвхөн задардаг хуулбаруудаас; аргачлал — бусадтайгаа хамгийн төстэй текст</td></tr>
<tr><td>Шатлал задрахгүй / илүү мөртэй (master эвдэрсэн)</td><td class="w">нийтлэг шатлал — засах шаардлагагүй, master-ийг гараар засна</td></tr>
<tr><td>Шатлал задардаг, өөр (санаатай)</td><td class="w">тухайн үйл ажиллагаанд дарна (activity.yaml)</td></tr>
<tr><td>Хамрах хугацаа хоосон / өөр</td><td class="w">хоосон бол нийтлэгийнх, өөр бол дарна</td></tr>
<tr><td>Автоматжуулах зөрүүтэй (act_01 «Тийм», act_06 «хоосон»)</td><td class="w">тодорхойлолтод SQL байвал бүх үйл ажиллагаанд автомат</td></tr>
<tr><td>Нэрийн төгсгөлөөрөө ялгаатай (…-УБ / …-ОН)</td><td class="w">тусдаа үзүүлэлт; SQL-ийг нэг удаа бичээд sql_from + params</td></tr>
<tr><td>Төстэй нэр (≥ 0.9)</td><td class="w">автоматаар нэгтгэхгүй — хүн шалгах</td></tr>
</table></div>
<h2>Нийтлэг тодорхойлолтын зөрүү (мөрийн тоо)</h2><div class="wrap"><table>{kinds_html}</table></div>
<h2>Нийтлэг тодорхойлолт ({len(common)})</h2>{''.join(rows_html)}
<h2>Нэг SQL + параметрээр дахин ашиглах боломжтой «гэр бүл» ({len(fam)}, {sum(len(ds) for _, ds in fam)} үзүүлэлт)</h2>
<div class="wrap"><table><tr><th>суурь нэр</th><th>хувилбар</th><th>бүлэг</th></tr>{fam_html}</table></div>
<h2>Төстэй нэр — хүн шалгах ({len(near)})</h2>
<div class="wrap"><table><tr><th>төстэй</th><th>нэр</th><th>нэр</th></tr>{near_html}</table></div>
<h2>Үйл ажиллагаа бүрт</h2>
<div class="wrap"><table><tr><th>бүлэг</th><th>үйл ажиллагаа</th><th>өөрийн</th><th>нийтлэг</th><th>нийт</th></tr>{act_html}</table></div>
</main></body></html>"""


CSS = """
:root{--bg:#f4f6f5;--card:#fff;--ink:#16211e;--mute:#5d6b67;--line:#dde3e0;--acc:#0f6b5c;--warn:#a15c07;--warnbg:#fdf1de;
--chip:#e9efed;--f-display:"Onest","IBM Plex Sans",system-ui,sans-serif;--f-body:"IBM Plex Sans",system-ui,sans-serif;
--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1513;--card:#161e1b;--ink:#e6ece9;--mute:#93a29d;
--line:#26302c;--acc:#5cc3ad;--warn:#f0b45a;--warnbg:#3a2a12;--chip:#222c28;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1513;--card:#161e1b;--ink:#e6ece9;--mute:#93a29d;--line:#26302c;--acc:#5cc3ad;
--warn:#f0b45a;--warnbg:#3a2a12;--chip:#222c28;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--f-body)}
main{max-width:1180px;margin:0 auto;padding:28px 16px 64px;display:grid;gap:12px}main>*{min-width:0}
h1{font:600 26px/1.2 var(--f-display);margin:0;text-wrap:balance}h2{font:600 17px/1.3 var(--f-display);margin:20px 0 0}
.eyebrow{font:600 11px/1 var(--f-body);letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}
p.lead{color:var(--mute);margin:0;max-width:80ch}.mute{color:var(--mute)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;display:grid;gap:2px}
.card b{font:600 22px/1.2 var(--f-mono);font-variant-numeric:tabular-nums}.card span{color:var(--mute);font-size:12px}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:6px 10px;border-bottom:1px solid var(--line);
text-align:left;vertical-align:top;white-space:nowrap}tr:last-child td{border-bottom:0}
th{color:var(--mute);font-size:11px;letter-spacing:.04em;text-transform:uppercase}
td.num{text-align:right;font:13px var(--f-mono);font-variant-numeric:tabular-nums}td.w{white-space:normal;min-width:240px}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px}
summary{cursor:pointer;line-height:1.9}summary:focus-visible{outline:2px solid var(--acc)}
code{font:12px var(--f-mono)}.b{display:inline-block;font-size:11px;padding:0 7px;border-radius:999px;
background:var(--chip);margin-left:4px}.b.warn{background:var(--warnbg);color:var(--warn)}
"""
