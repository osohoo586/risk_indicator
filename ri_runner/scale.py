"""Оноо: DaHUB-ийн scoring-rules.ts-ийн computeScoreFromScale-ийн Python хуулбар + master-ийн шатлалын
текстийг ("1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош") DaHUB-ийн score_scale JSON болгох parser.

DaHUB-ийн дүрэм:
  - numericRules: {min, max, score, label} — min ≤ x < max, оноо ихээс нь эхэлж шалгана
  - stringRules:  {values, matchType: exact|contains, score, label} — зай/NBSP нормчилно
  - score 0 = "Үнэлэхгүй" (жингээс хасагдана)
  - хоосон утга: null_empty_score = unelehgui (default) | "1" | "5"
  - manual / no_score төрөлд автомат оноо тооцохгүй (None)
Нэмэлт (RA): "unit": "percent" — шатлал хувиар бичигдсэн, утга харьцаагаар (0.9746) ирвэл ×100.
"""
import re

UNELEHGUI = "Үнэлэхгүй"


# ── DaHUB computeScoreFromScale ───────────────────────────────────────────────
def _norm(s: str) -> str:
    return re.sub(r"[\s ​]+", " ", str(s)).strip()


def _null_policy(scale: dict) -> str:
    v = scale.get("null_empty_score")
    if v in ("1", "5", "unelehgui"):
        return v
    if scale.get("null_is_unelehgui") is False:
        return "5"
    return "unelehgui"


def _empty(scale: dict):
    p = _null_policy(scale)
    if p == "5":
        return 5, "Мэдээлэл байхгүй"
    if p == "1":
        return 1, "Мэдээлэл байхгүй"
    return UNELEHGUI, "Мэдээлэл байхгүй"


def _numeric(rules: list, raw: str):
    try:
        n = float(raw.replace(",", "."))
    except ValueError:
        return None
    if n != n:
        return None
    for r in sorted(rules, key=lambda r: -r["score"]):
        lo, hi = r.get("min"), r.get("max")
        if (lo is None or n >= lo) and (hi is None or n < hi):
            return (UNELEHGUI if r["score"] == 0 else r["score"]), r.get("label")
    return None


def _string(rules: list, raw: str):
    t = _norm(raw)
    for r in rules:
        vals = r.get("values") or []
        if r.get("matchType") == "contains":
            hit = any(_norm(v) in t for v in vals)
        else:
            hit = any(_norm(v) == t for v in vals)
        if hit:
            return (UNELEHGUI if r["score"] == 0 else r["score"]), r.get("label")
    return _fuzzy(rules, t)


def _fuzzy(rules: list, t: str):
    """Үсгийн алдаа ("Сайжрулах" ↔ "Сайжруулах"): 8+ тэмдэгттэй ангилал ≥ 0.92 төстэй бол тэр мөр (хамгийн төстэй)."""
    import difflib
    if len(t) < 8:
        return None
    best, best_r = None, 0.92
    for r in rules:
        for v in r.get("values") or []:
            v = _norm(v)
            if len(v) >= 8:
                ratio = difflib.SequenceMatcher(None, v.lower(), t.lower()).ratio()
                if ratio >= best_r:
                    best, best_r = r, ratio
    if best is None:
        return None
    return (UNELEHGUI if best["score"] == 0 else best["score"]), best.get("label")


_POSITIVE = re.compile(r"(^|[^а-яөү])(тийм|гарсан|илэрсэн|зөрчилтэй)", re.I)
_NEGATIVE = re.compile(r"үгүй|гараагүй|илрээгүй|зөрчилгүй", re.I)


def _yes_no(rules: list, raw: str):
    """Тийм/Үгүй (гарсан/гараагүй) ангилалд ТОО ирвэл: > 0 → эерэг (Тийм) мөр, 0 → сөрөг (Үгүй) мөр."""
    try:
        n = float(raw.replace(",", "."))
    except ValueError:
        return None
    for r in rules:
        text = " ".join([str(r.get("label") or "")] + [str(v) for v in r.get("values") or []]).lower()
        if (n > 0 and _POSITIVE.search(text) and not _NEGATIVE.search(text)) or (n == 0 and _NEGATIVE.search(text)):
            return (UNELEHGUI if r["score"] == 0 else r["score"]), r.get("label")
    return None


def compute_score(scale: dict | None, value, result_type: str | None = None, value_unit: str = "ratio"):
    """(score, label). score: 1–5 | "Үнэлэхгүй" | None (автомат оноо байхгүй)."""
    if not scale or scale.get("type") in ("no_score", "manual", "multi_subid"):
        return None, None
    raw = "" if value is None else str(value).strip()
    if not _norm(raw):
        return _empty(scale)
    if (scale.get("unit") == "percent" and value_unit == "ratio"
            and re.fullmatch(r"-?\d+(?:[.,]\d+)?(?:[eE]-?\d+)?", raw)):
        raw = repr(float(raw.replace(",", ".")) * 100)
    is_str = str(result_type or "").upper() == "STRING"
    t = scale.get("type")
    num = scale.get("numericRules") or scale.get("rules") or []
    st = scale.get("stringRules") or scale.get("rules") or []
    if t == "string":
        rules = scale.get("stringRules") or scale.get("rules") or []
        hit = _string(rules, raw) or _yes_no(rules, raw)
        if hit:
            return hit
    elif t == "numeric":
        if is_str and (hit := _string(st, raw)):
            return hit
        if hit := _numeric(num, raw):
            return hit
        if not is_str and (hit := _string(st, raw)):
            return hit
    elif t == "both":
        try:
            float(raw.replace(",", "."))
            is_num = True
        except ValueError:
            is_num = False
        if (is_str or not is_num) and (hit := _string(scale.get("stringRules") or [], raw)):
            return hit
        if hit := _numeric(scale.get("numericRules") or [], raw):
            return hit
        if hit := _string(scale.get("stringRules") or [], raw):
            return hit
    return UNELEHGUI, "тодорхойлогдоогүй"


def risk_level(total, high: float = 3.5, medium: float = 2.5) -> str:
    """DaHUB-ийн riskLevel: ≥3.5 Өндөр, ≥2.5 Дунд, бусад Бага."""
    if total is None or total != total:
        return ""
    if total >= high:
        return "Өндөр"
    if total >= medium:
        return "Дунд"
    return "Бага"


# ── Master-ийн шатлалын текст → DaHUB score_scale ─────────────────────────────
# Мөр бүр "ОНОО-тайлбар". Тайлбар нэг ба түүнээс олон хүрээ ("0-1 жил and 5-с дээш жил"), эсвэл ангилал.
# Хилийн дүрэм (master-ийн бичлэгээс):
#   "a-b"                         a, b хоёулаа орно; хоёр хүрээ нийлсэн цэг ("0-1", "1-2" → 1) дараагийнх
#   "N ба/болон түүнээс дээш|доош" N орно
#   "N-аас бага"                  N орохгүй
#   "N-с дээш", "N-с доош", "N хүртэл"  N-ийг өөр мөр (жнь "2-3") багтаасан бол орохгүй, эс бөгөөс орно
#   "1-1" (хувьтай шатлалд)       100%
#   0-мөр "/гараагүй/, /Үгүй/, /зөрчилгүй/" утга 0 → Үнэлэхгүй (бусад мөр 0-ээс их)
# Хүрээний хоорондох завсар доод мөрт, хамгийн бага/их мөрийн гадна утга тэр мөрт.
_NUM = r"(\d+(?:[.,]\d+)?)"
_LINE = re.compile(r"^\s*([0-5])\s*[-–.)]\s*(.+?)\s*$")
_EPS = 1e-9
# "16 цагаас дээш", "3 жилээс дээш", "20-иос дээш", "10 доош цаг"
_ABOVE = re.compile(_NUM + r"\s*%?\s*[-–]?\s*[а-яөү]{0,10}\s*(?:дээш|илүү|давсан|(?<![а-яөү])их(?![а-яөү]))")
_BELOW = re.compile(_NUM + r"\s*%?\s*[-–]?\s*[а-яөү]{0,10}\s*(?:доош|бага)")
_INCL_ABOVE = re.compile(_NUM + r"\s*%?\s*(?:ба|болон)?\s*түүнээс\s+(?:дээш|их)")
_INCL_BELOW = re.compile(_NUM + r"\s*%?\s*(?:ба|болон)?\s*түүнээс\s+(?:доош|бага)")
_STRICT_BELOW = re.compile(_NUM + r"\s*%?\s*[-–]?\s*[а-яөү]{0,10}(?:аас|ээс|оос|өөс|иас|иос)\s+бага")
_UPTO = re.compile(_NUM + r"\s*%?\s*(?:[а-яөү]+\s+)?хүртэл")
_RANGE = re.compile(_NUM + r"\s*%?\s*[-–]\s*" + _NUM)
_ZERO_WORDS = re.compile(r"гараагүй|зөрчилгүй|/\s*үгүй\s*/", re.I)


def _f(s: str) -> float:
    return float(s.replace(",", "."))


def _split_lines(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"[\r\n|]+", text or "") if p.strip()]
    if len(parts) > 1:
        return parts                    # мөр бүр нэг оноо ("…бүртгэлээр 2-3 гомдол" доторх 2-3 оноо биш)
    # Бүх шатлал НЭГ мөрөнд ("1-96.1%-аас дээш 3-90.1%-96% 5-90%-с доош") бол оноо бүрээр хуваана
    return [x.strip() for x in re.split(r"(?<!and)\s+(?=[0-5]\s*-\s*\S)", parts[0]) if x.strip()] if parts else []


def _segment(seg: str):
    """Нэг хүрээ: (lo, lo_incl, hi, hi_incl, soft_lo, soft_hi, pct) эсвэл None (тоо биш)."""
    b = seg.lower().replace("−", "-").replace("–", "-").replace(" ", " ")
    pct = "%" in b or "хувь" in b
    if m := _INCL_ABOVE.search(b):
        return _f(m.group(1)), True, None, False, False, False, pct
    if m := _INCL_BELOW.search(b):
        return None, False, _f(m.group(1)), True, False, False, pct
    if m := _STRICT_BELOW.search(b):
        return None, False, _f(m.group(1)), False, False, False, pct     # хатуу: N орохгүй
    if m := _RANGE.search(b):
        lo, hi = sorted((_f(m.group(1)), _f(m.group(2))))
        # "19-с дээш" нь хүрээ биш (19 ба "с дээш")
        if not re.match(r"\s*(?:аас|ээс|оос|өөс|иас|иос|с)?\s*(?:дээш|доош|бага|их)", b[m.end():]) \
                or re.search(_NUM + r"\s*%?\s*-\s*" + _NUM + r"\s*%", b):
            return lo, True, hi, True, False, False, pct
    if m := _ABOVE.search(b):
        return _f(m.group(1)), True, None, False, True, False, pct
    if m := _BELOW.search(b):
        return None, False, _f(m.group(1)), True, False, True, pct
    if m := _UPTO.search(b):
        return None, False, _f(m.group(1)), True, False, True, pct
    nums = re.findall(_NUM, b)
    units = r"(жил|цаг|өдөр|өдөрт|хоног\w*|хувь|сар|удаа|ширхэг)"
    if len(nums) == 1 and not re.search(r"[а-яөүa-z]{4,}", re.sub(units, "", b)):
        n = _f(nums[0])
        return n, True, n, True, False, False, pct
    return None


def parse_scale_text(text: str) -> tuple[dict | None, str | None]:
    """(score_scale dict, алдаа/анхааруулга эсвэл None). Тоон шатлал → numeric/both, бусад → string (ангилал)."""
    lines = _split_lines(text)
    items, unknown = [], []
    for ln in lines:
        m = _LINE.match(ln)
        if m:
            items.append((int(m.group(1)), m.group(2).strip()))
        elif ln.strip():
            unknown.append(ln.strip()[:40])
    if not items:
        return None, "оноо-тайлбар хэлбэр олдсонгүй" + (f" ({unknown[0]})" if unknown else "")

    intervals, strings, zero_rule = [], [], False
    for score, body in items:
        low = body.lower()
        if score == 0 and _ZERO_WORDS.search(low):
            zero_rule = True
        if re.match(r"^үнэлэхгүй", low):
            strings.append({"values": [body], "matchType": "exact", "score": score, "label": body})
            continue
        segs = [x for x in re.split(r"\s+and\s+|\s*/\s*(?=[а-яөүА-ЯӨҮ])", body) if x.strip()]
        found = False
        for seg in segs:
            iv = _segment(seg)
            if iv is None:
                if found or len(segs) > 1:          # "…/удирдлага байхгүй/" — нэмэлт ангилал
                    strings.append({"values": [seg.strip(" ./")], "matchType": "contains", "score": score,
                                    "label": body})
                continue
            found = True
            intervals.append({"score": score, "label": body, "iv": list(iv)})
            tail = re.search(r",\s*([^\d,]{4,}?)\s*\.?$", seg)        # "3 жилээс дээш, аудит ороогүй" — нэмэлт ангилал
            if tail:
                strings.append({"values": [tail.group(1).strip()], "matchType": "contains", "score": score,
                                "label": body})
        if not found:
            strings.append({"values": [re.sub(r"\s*/.*?/\s*", "", body).strip(" ."), body],
                            "matchType": "exact", "score": score, "label": body})

    if not intervals or len({i["score"] for i in intervals}) < 2 and len(intervals) < 2:
        cats = strings + [{"values": [i["label"]], "matchType": "exact", "score": i["score"], "label": i["label"]}
                          for i in intervals]
        return {"type": "string", "stringRules": cats}, (f"танигдаагүй мөр: {unknown}" if unknown else None)

    pct = any(i["iv"][6] for i in intervals)
    if pct:
        # %-тай шатлал дахь %-гүй ганц тоо нь бутархай: "1-1" = 100%, "4-0.05" = 5%
        for i in intervals:
            lo, _, hi, _, _, _, ipct = i["iv"]
            if not ipct and lo is not None and lo == hi and 0 < lo <= 1:
                i["iv"][0] = i["iv"][2] = lo * 100
    rules = _to_rules(intervals, zero_rule)
    scale = {"type": "both" if strings else "numeric", "numericRules": rules}
    if strings:
        scale["stringRules"] = strings
    if pct:
        scale["unit"] = "percent"
    return scale, (f"танигдаагүй мөр: {unknown}" if unknown else None)


def _to_rules(intervals: list, zero_rule: bool) -> list:
    """Хилийн дүрэм → DaHUB numericRules ([min, max)), завсар хаах, гадна утга."""
    # Зөөлөн хил (дээш/доош/хүртэл): өөр мөр яг тэр тоог багтаасан бол орохгүй
    for i in intervals:
        lo, lo_in, hi, hi_in, soft_lo, soft_hi, _ = i["iv"]
        others = [o["iv"] for o in intervals if o is not i]
        if soft_lo and lo is not None and any(o[2] == lo and o[3] for o in others):
            i["iv"][1] = False
        if soft_hi and hi is not None and any(o[0] == hi and o[1] for o in others):
            i["iv"][3] = False
    # Нийлсэн цэг ("0-1 жил" ба "1-2 жил"-ийн 1) дараагийн хүрээнд: [0, 1), [1, 2]
    for i in intervals:
        for o in intervals:
            if o is not i and i["iv"][2] is not None and i["iv"][2] == o["iv"][0] and i["iv"][3] and o["iv"][1] \
                    and (i["iv"][0] is None or i["iv"][0] < i["iv"][2]):
                i["iv"][3] = False
                i["iv"].append("touch")
    rules = []
    for i in intervals:
        lo, lo_in, hi, hi_in = i["iv"][:4]
        rules.append({"min": None if lo is None else (lo if lo_in else lo + _EPS),
                      "max": None if hi is None else (hi + _EPS if hi_in else hi),
                      "score": i["score"], "label": i["label"],
                      "_strict": hi is not None and not hi_in and "touch" not in i["iv"]})
    rules.sort(key=lambda r: (float("-inf") if r["min"] is None else r["min"]))
    for a, b in zip(rules, rules[1:]):
        if a["max"] is not None and b["min"] is not None and a["max"] < b["min"]:
            if a.pop("_strict", False):
                b["min"] = a["max"]                   # "10-аас бага" ба "11-13": 10 → дээд мөр (бага нь 10-ыг хассан)
            else:
                a["max"] = b["min"]                   # "10%-12%" ба "13%-15%": 12.5 → доод мөр
    for r in rules:
        r.pop("_strict", None)
    lowest = min(rules, key=lambda r: float("-inf") if r["min"] is None else r["min"])
    highest = max(rules, key=lambda r: float("inf") if r["max"] is None else r["max"])
    if highest["max"] is not None:
        highest["max"] = None                         # хамгийн дээд мөрөөс их утга (105% орон тоо) → тэр мөр
    if zero_rule:
        for r in rules:
            if r["min"] is None or r["min"] <= 0:
                r["min"] = _EPS                       # 0 = "гараагүй" → Үнэлэхгүй
        rules.append({"min": 0.0, "max": _EPS, "score": 0, "label": "0 (гараагүй)"})
    elif lowest["min"] is not None:
        lowest["min"] = None                          # хамгийн доод мөрөөс бага утга → тэр мөр
    return rules
