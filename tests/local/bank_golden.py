"""ЭТАЛОН: demo DB-ийн түүхий мөрүүдээс (bank_demo.build()) үзүүлэлт бүрийн зөв хариуг SQL-ээс ҮЛ ХАМААРАН
энгийн Python-оор тооцно. demo_check.py нь runner-ийн ClickHouse-д бичсэнтэй мөр бүрээр тулгана.

Тооцооллын тодорхойлолт (SQL-ийн тайлбартай ижил, гэхдээ тусдаа бичигдсэн):
  ажиллаж байгаа (өдөр x)  EMPLOYEE_HISTORY START_DATE ≤ x ≤ NVL(END_DATE, ∞)
  гарсан [a, b]            ERP_EMPLOYEE.END_DATE ∈ [a, b], тухайн өдрийн томилгооны SOLID-д
  хугацаа                  report = улирлын эхнээс (-p 2026-Q3), last_year = d − 1 жил + 1 өдөр,
                           since_audit = аудитын огноо (d-ээс хойш бол last_year), latest = сүүлийн үе
  улирлын тоо              [эхлэл, d]-д хамаарах календарийн улирал
  үйл ажиллагаа            тайлант өдрийн MAIN snapshot-ийн BRANCHID-ийн SOLID-ууд: Σ тоологч / Σ хуваарь
                           (тоо бол Σ утга), BANK үзүүлэлт — банк нийт

Оноо: мастерийн шатлалыг ГАРААР уншиж бичсэн босго (CANON) — parser-ээс үл хамаарна. Мастерт өөр
(эвдэрсэн) бичиглэлтэй үзүүлэлтийг "МАСТЕР" гэж тэмдэглэнэ (тайланд тусад нь).
"""
import csv
import datetime as dt
from collections import defaultdict

import bank_demo as B

D = dt.date


# ── Огноо ─────────────────────────────────────────────────────────────────────
def quarter_start(d: dt.date) -> dt.date:
    return D(d.year, 3 * ((d.month - 1) // 3) + 1, 1)


def year_back(d: dt.date) -> dt.date:
    try:
        return d.replace(year=d.year - 1) + dt.timedelta(days=1)
    except ValueError:
        return D(d.year - 1, 2, 28) + dt.timedelta(days=1)


def n_quarters(a: dt.date, b: dt.date) -> int:
    return max(1, (b.year * 4 + (b.month - 1) // 3) - (a.year * 4 + (a.month - 1) // 3) + 1)


def start_for(period: str, d: dt.date, audit: dt.date | None) -> dt.date:
    if period == "last_year":
        return year_back(d)
    if period == "since_audit":
        return audit if audit and audit <= d else year_back(d)
    return quarter_start(d)


# ── Байгууллага ───────────────────────────────────────────────────────────────
def activity_map() -> dict[int, dict]:
    with (B.DEMO_DIR / "activity_map.csv").open(encoding="utf-8-sig") as f:
        return {int(r["GROUP_NO"]): {"branch": r["BRANCHID"], "audit": D.fromisoformat(r["LAST_AUDIT_DATE"])
                                     if r["LAST_AUDIT_DATE"] else None} for r in csv.DictReader(f)}


def sols_of(data, branch_id, d) -> set[str]:
    snaps = sorted({r[0] for r in data["COREMIS.MAIN"]})
    past = [s for s in snaps if s <= d]
    snap = past[-1] if past else snaps[0]
    return {str(r[1]) for r in data["COREMIS.MAIN"] if r[0] == snap and str(r[2]) == str(branch_id)}


# ── Хүний нөөц ────────────────────────────────────────────────────────────────
class HR:
    def __init__(self, data):
        self.sol_of_dept = {r[0]: r[2] for r in data["ERP.HR_ORG_DEPARTMENT"]}
        self.pos = {r[0]: (r[2], r[3] == "Y") for r in data["ERP.ERP_HR_POSITION"]}
        self.emp = {r[0]: {"hire": r[6], "end": r[7]} for r in data["ERP.ERP_EMPLOYEE"]}
        self.hist = [{"emp": r[1], "sol": self.sol_of_dept[r[2]], "title": self.pos[r[3]][0],
                      "mgr": self.pos[r[3]][1], "start": r[5], "end": r[6]} for r in data["ERP.EMPLOYEE_HISTORY"]]
        self.sols = sorted({str(s) for s in self.sol_of_dept.values()})

    @staticmethod
    def on(h, x):
        return h["start"] <= x and (h["end"] is None or h["end"] >= x)

    def at(self, x):
        return [h for h in self.hist if self.on(h, x)]

    def flow(self, a, b):
        """{sol: [hc_start, hc_end, sep, hc_start_mgr, hc_end_mgr, sep_mgr]}"""
        out = defaultdict(lambda: [0] * 6)
        for h in self.hist:
            s = str(h["sol"])
            end = self.emp[h["emp"]]["end"]
            for k, hit in ((0, self.on(h, a)), (1, self.on(h, b)),
                           (2, end is not None and a <= end <= b and self.on(h, end))):
                if hit:
                    out[s][k] += 1
                    if h["mgr"]:
                        out[s][k + 3] += 1
        return out


# ── Нийтлэг тооцоолол (SOL бүрээр): {sol: {"num", "den", "value", "text"}} ────
def _row(num=None, den=None, value=None, text=None):
    if value is None and num is not None and den:
        value = num / den
    return {"num": num, "den": den, "value": value, "text": text}


def calc_rows(data, hr: HR, calc: str, start: dt.date, d: dt.date, params: dict | None = None,
              amap: dict | None = None) -> tuple[str, dict]:
    """(түвшин SOL / BANK / UNIT, {entity_id: мөр})."""
    out = {}
    if calc in ("tenure", "mgr_tenure"):
        mgr = calc == "mgr_tenure"
        acc = defaultdict(lambda: [0.0, 0])
        for h in hr.at(d):
            if h["mgr"] == mgr:
                since = h["start"] if mgr else hr.emp[h["emp"]]["hire"]
                acc[str(h["sol"])][0] += (d - since).days / 365.25
                acc[str(h["sol"])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if calc == "appraisal":
        cyc = max(r[2] for r in data["ERP.ERP_HR_APPRAISAL"] if r[2] <= d)
        score = {r[1]: r[3] for r in data["ERP.ERP_HR_APPRAISAL"] if r[2] == cyc}
        acc = defaultdict(lambda: [0.0, 0])
        for h in hr.at(d):
            if h["emp"] in score:
                acc[str(h["sol"])][0] += score[h["emp"]] / 100
                acc[str(h["sol"])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if calc == "complaints":
        q = n_quarters(start, d)
        cnt, dag = defaultdict(int), set()
        for r in data["COREMIS.CUSTOMER_COMPLAINT"]:
            if start <= r[2] <= d:
                if r[3] == "ХҮГ" and r[4] == "Y":
                    cnt[str(r[1])] += 1
                if r[3] == "ДАГ" and r[5] == "ШИЙДВЭРЛЭСЭН":
                    dag.add(str(r[1]))
        for r in data["FINACLE.SOL"]:
            s = str(r[0])
            out[s] = _row(cnt[s], None, cnt[s] / q, "ДАГ-т гомдол ирж, шалгагдсан." if s in dag else None)
        return "SOL", out
    if calc == "training":
        hours = defaultdict(float)
        for r in data["ERP.ERP_HR_TRAINING"]:
            if start <= r[4] <= d:
                hours[r[1]] += r[5]
        acc = defaultdict(lambda: [0.0, 0])
        for h in hr.at(d):
            acc[str(h["sol"])][0] += hours.get(h["emp"], 0.0)
            acc[str(h["sol"])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if calc == "staffing":
        plan = defaultdict(int)
        for r in data["ERP.ERP_HR_STAFF_PLAN"]:
            if r[4] <= d and (r[5] is None or r[5] >= d):
                plan[str(hr.sol_of_dept[r[1]])] += r[3]
        act = defaultdict(int)
        for h in hr.at(d):
            act[str(h["sol"])] += 1
        return "SOL", {s: _row(act[s], p, act[s] / p if p else None) for s, p in plan.items()}
    if calc == "turnover":
        return "SOL", {s: _row(f[2], (f[0] + f[1]) / 2) for s, f in hr.flow(start, d).items()}
    if calc == "ethics":
        cnt = defaultdict(int)
        for r in data["ERP.ERP_HR_DISCIPLINE"]:
            if r[3] == "ЁС ЗҮЙ" and start <= r[2] <= d:
                for h in hr.hist:
                    if h["emp"] == r[1] and hr.on(h, r[2]):
                        cnt[str(h["sol"])] += 1
        return "SOL", {s: _row(None, None, cnt[s]) for s in hr.sols}
    if calc == "green":
        green = _loan_sums(data, d, lambda b: b["green"])
        return "SOL", {str(r[1]): _row(green.get(str(r[1]), 0.0), r[2]) for r in data["COREMIS.GREEN_LOAN_PLAN"]
                       if r[0] == d}
    if calc in GRC_LOGIC:
        return grc_rows(data, hr, calc, start, d, params or {})
    return own_rows(data, hr, calc, start, d, params or {}, amap or {})


def _loan_book(data, d):
    lam = {r[0]: r[5] == "Y" for r in data["FINACLE.LAM"]}
    gam = {r[0]: (str(r[3]), r[4]) for r in data["FINACLE.GAM"]}
    return [{"sol": gam[r[1]][0], "cls": r[2], "out": r[3], "prov": r[4], "green": lam.get(r[1], False)}
            for r in data["FINACLE.LOAN_CLASS_HIST"] if r[0] == d and gam[r[1]][1] == "LAA"]


def _loan_sums(data, d, pred, field="out"):
    acc = defaultdict(float)
    for b in _loan_book(data, d):
        if pred(b):
            acc[b["sol"]] += b[field]
    return acc


# Тооцооллын логик — үзүүлэлтийн НЭРЭЭР (dedup.norm_key): ID нь бүтэц өөрчлөгдөхөд (SH_NNN, RI_GG_NNNN) өөрчлөгдөж
# болох ч нэр тогтвортой. Утга нь доорх calc_rows / own_rows-ийн салбар.
LOGIC = {
    "ажилтнуудын ажилласан жилийн дундаж": "tenure", "удирдах ажилтны ажилласан жилийн дундаж": "mgr_tenure",
    "ажилтнуудын ажлын гүйцэтгэлийн үнэлгээний дундаж": "appraisal", "гарсан гомдлын тоо": "complaints",
    "нэг ажилтанд ногдох сургалтын цаг": "training", "орон тоо бүрэн эсэх": "staffing",
    "хүний нөөцийн эргэц": "turnover", "ес зүйн зөрчил": "ethics", "нийт ногоон зээлийн төлөвлөгөөний биелэлт": "green",
    "зээлийн төлөвлөгөөний биелэлт": "GL3003a", "эх үүсвэрийн төлөвлөгөөний биелэлт": "GL3003a",
    "лизингийн багцын төлөвлөгөөни биелэлт": "GL3003a",
    "дотоод үнэлгээний ашгийн төлөвлөгөөний биелэлт": "IN2003", "алтны арилжааны ашиг-корпорэйт-уудбх": "IN2003",
    "лизингийн хүүгийн орлогын төлөвлөгөөний биелэлт": "IN2003", "күб-н шимтгэлийн орлого-корпорейт": "IN2003",
    "ахзээл/нийт зээл": "loan_attention", "чанаргүй зээл/нийт зээл": "loan_npl",
    "зээлийн эрсдэлийн сан/чанаргүй зээл": "loan_provision", "эргэн хяналтын чанар-corp": "monitoring",
    "зээл шийдвэрлэх процессын хурд": "decision_speed",
    "дижитал идэвхтэй харилцагчийн тоон төлөвлөгөөний биелэлт-корпорэйт": "digital_active",
    "нийт идэвхтэй харилцагчийн тоон төлөвлөгөөний биелэлт-корпорэйт": "active_customers",
    "бүртгэлийн баримтад зөрчил илэрсэн эсэх/хбг-хххх/": "doc_check", "зхб-ийн материал зөрчилтэй байх": "lc_check",
    "абх-дохиоллын түгшүүрийн зөрчил хураангуй": "jira_alarm",
    "картын залилангийн гүйлгээний хувь(demo,clickhouse source)": "card_fraud",
    "банкны удирдах ажилтнуудын хүний нөөцийн эргэц": "bank_mgr_turnover",
    "банкны ажилтнуудын хүний нөөцийн эргэц": "bank_turnover",
    "ажилтнуудын ажлын гүйцэтгэлийн дундаж үнэлгээ": "bank_appraisal",
    "хүний нөөцийн нэг ажилтанд ногдох нийт ажилтнуудын тоо": "hr_ratio",
    # master-т гарын, demo-д системээс (GRC, ERP, JIRA, MAIN)
    "action plan биелэлт": "action_plan", "бүтцийн өөрчлөлт хийгдсэн эсэх": "structure_change",
    "дүрэм журам шинэчлэгдсэн эсэх": "policy_age", "монгол банкны үнэлгээ": "mb_review",
    "хөндлөнгийн аудитын зөвлөмж": "external_audit", "өмнөх аудитаас хойшхи хугацаа": "since_last_audit",
    "өмнөх аудитын үнэлгээ": "audit_rating", "өндөр эрсдэлтэй асуудлын тоо": "high_risk_share",
    "follow up үнэлгээ": "follow_up", "зайны аудитаар зөрчил гарсан эсэх": "remote_audit",
    "мэдлэгийн түвшин": "knowledge", "банкны нууцын зэрэглэлтэй мэдээлэл задруулсан эсэх": "infosec",
    "харилцагчийн нууцын зэрэглэлтэй мэдээлэл задруулсан эсэх": "infosec",
    "салбар,тооцооны төвийн захирлуудын орон тоо сул байсан хугацаа": "director_vacancy",
}
MB_TEXT = {1: "Сайн", 2: "Хэвийн", 3: "Дунд", 4: "Хангалтгүй", 5: "Муу"}
EXT_TEXT = {1: "Бага эрсдэлтэй зөвлөмж өгсөн", 3: "Дунд эрсдэлтэй зөвлөмж өгсөн", 5: "Өндөр эрсдэлтэй зөвлөмж өгсөн"}
RATING_TEXT = {1: "Хангалттай", 3: "Сайжрулах шаардлагатай", 5: "Хангалтгүй"}
REMOTE_TEXT = {5: "Зайны аудитаар зөрчил илэрч Илтгэх хуудас бичигдсэн", 4: "Нэг төрлийн зөрчил давтагдан гарсан",
               3: "Нэг төрлийн зөрчил давтагдаагүй, өөр төрлийн зөрчил аудит дарааллан гарсан",
               2: "Зайн аудитаар зөрчил гарсан боловч зөрчлийг арилгасан", 1: "Зөрчил гараагүй"}
INFOSEC_TEXT = {("БАНК", 4): "Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан",
                ("БАНК", 5): "Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан "
                             "зөрчил давтагдсан",
                ("ХАРИЛЦАГЧ", 4): "Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, "
                                  "гадагш гаргасан",
                ("ХАРИЛЦАГЧ", 5): "Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, "
                                  "гадагш гаргасан зөрчил давтагдсан"}


def last_audits(data, d) -> dict:
    """{BRANCHID: (engagement_id, end_date, rating)} — тайлант өдрөөс өмнөх сүүлийн дотоод аудит."""
    out = {}
    for r in sorted(data["GRC.AUDIT_ENGAGEMENT"], key=lambda r: (r[3], r[0])):
        if r[3] <= d:
            out[str(r[1])] = (r[0], r[3], r[4])
    return out


def branches_at(data, d) -> set[str]:
    snaps = sorted({r[0] for r in data["COREMIS.MAIN"]})
    past = [x for x in snaps if x <= d]
    snap = past[-1] if past else snaps[0]
    return {str(r[2]) for r in data["COREMIS.MAIN"] if r[0] == snap}


def grc_rows(data, hr, logic: str, start: dt.date, d: dt.date, params: dict) -> tuple[str, dict]:
    """master-т гарын боловч системийн өгөгдлөөс тооцох үзүүлэлтүүд (GRC, ERP, JIRA, MAIN)."""
    allb = branches_at(data, d)
    la = last_audits(data, d)
    if logic == "action_plan":
        acc = defaultdict(lambda: [0, 0])
        for r in data["JIRA.ACTION_PLAN"]:
            if start <= r[4] <= d:
                acc[str(r[1])][0] += r[5] is not None and r[5] <= r[4]
                acc[str(r[1])][1] += 1
        return "ACTIVITY", {b: _row(n, c) for b, (n, c) in acc.items()}
    if logic == "structure_change":
        snaps = sorted({r[0] for r in data["COREMIS.MAIN"]})
        pick = lambda x: ([s for s in snaps if s <= x] or [snaps[0]])[-1]       # noqa: E731
        t0, t1 = pick(start), pick(d)
        u0 = {(str(r[2]), r[1]): r[4] for r in data["COREMIS.MAIN"] if r[0] == t0}
        u1 = {(str(r[2]), r[1]): r[4] for r in data["COREMIS.MAIN"] if r[0] == t1}
        changed = defaultdict(list)
        for k in set(u0) ^ set(u1):
            changed[k[0]].append(u1.get(k) or u0.get(k))
        out = {}
        for b in {k[0] for k in u1}:
            names = changed.get(b, [])
            text = ("Үнэлэхгүй /Үгүй/" if not names else
                    "Газар, хэлтэс" if any("алба" not in n.lower() for n in names) else "Алба")
            out[b] = _row(None, None, None, text)
        return "ACTIVITY", out
    if logic == "policy_age":
        acc = defaultdict(list)
        for r in data["GRC.POLICY_DOCUMENT"]:
            if r[3] <= d and r[4] <= d:
                acc[str(r[1])].append(r[4])
        return "ACTIVITY", {b: _row(None, None, (d - min(v)).days / 365.25) for b, v in acc.items()}
    if logic in ("mb_review", "external_audit"):
        who = "МБ" if logic == "mb_review" else "ХӨНДЛӨНГИЙН АУДИТ"
        hits = defaultdict(list)
        for r in data["GRC.EXTERNAL_REVIEW"]:
            if r[2] == who and start <= r[3] <= d:
                hits[str(r[1])].append(r)
        out = {}
        for b in allb:
            if logic == "mb_review":
                last = max(hits[b], key=lambda r: (r[3], r[0]))[4] if hits.get(b) else None
                out[b] = _row(None, None, None, MB_TEXT.get(last, "Үнэлэхгүй /МБ-ны шалгалт ороогүй /"))
            else:
                worst = max(r[4] for r in hits[b]) if hits.get(b) else None
                out[b] = _row(None, None, None, EXT_TEXT.get(worst, "Үнэлэхгүй /Хөндлөнгийн аудит/"))
        return "ACTIVITY", out
    if logic == "since_last_audit":
        return "ACTIVITY", {b: (_row(None, None, (d - la[b][1]).days / 365.25) if b in la else
                                _row(None, None, None, "аудит ороогүй")) for b in allb}
    if logic == "audit_rating":
        return "ACTIVITY", {b: _row(None, None, None, RATING_TEXT[la[b][2]] if b in la else
                                    "Үнэлэхгүй /Өмнө аудит хийж байгаагүй/") for b in allb}
    if logic in ("high_risk_share", "follow_up"):
        by_eng = defaultdict(list)
        for f in data["GRC.AUDIT_FINDING"]:
            by_eng[f[1]].append(f)
        out = {}
        for b in allb:
            if b not in la:
                out[b] = (_row(None, None, None, "Үнэлэхгүй /Өмнө аудит хийж байгаагүй/") if logic == "high_risk_share"
                          else _row(None, None, None, "Үнэлэхгүй"))
                continue
            fs = by_eng.get(la[b][0], [])
            if logic == "high_risk_share":
                n, c = sum(f[2] == "ӨНДӨР" for f in fs), len(fs)
                out[b] = _row(n, c, n / c if c else None)
            else:
                due = [f for f in fs if f[3] <= d]
                done = sum(f[4] == "ХЭРЭГЖСЭН" and f[5] is not None and f[5] <= f[3] for f in due)
                out[b] = _row(done, len(due), done / len(due)) if due else _row(None, None, None, "Үнэлэхгүй")
        return "ACTIVITY", out
    if logic == "remote_audit":
        worst = {}
        for r in data["GRC.REMOTE_AUDIT_CHECK"]:
            if start <= r[2] <= d:
                worst[str(r[1])] = max(worst.get(str(r[1]), 0), r[3])
        return "ACTIVITY", {b: _row(None, None, None, REMOTE_TEXT.get(w, "Зөрчил гараагүй")) for b, w in worst.items()}
    if logic == "knowledge":
        last = {}
        for r in sorted(data["ERP.ERP_HR_KNOWLEDGE_TEST"], key=lambda r: (r[2], r[0])):
            if r[2] <= d:
                last[r[1]] = r[3]
        acc = defaultdict(lambda: [0.0, 0])
        for h in hr.at(d):
            if h["emp"] in last:
                acc[str(h["sol"])][0] += last[h["emp"]] / 100
                acc[str(h["sol"])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if logic == "infosec":
        dtype = params.get("p_data_type")
        sev = {}
        for r in data["GRC.INFOSEC_INCIDENT"]:
            if r[3] == dtype and start <= r[2] <= d:
                sev[str(r[1])] = max(sev.get(str(r[1]), 0), r[4])
        return "SOL", {str(r[0]): _row(None, None, None, INFOSEC_TEXT[(dtype, 5 if sev[str(r[0])] >= 5 else 4)]
                                       if str(r[0]) in sev else "Үнэлэхгүй /Зөрчилгүй/") for r in data["FINACLE.SOL"]}
    if logic == "director_vacancy":
        pos = {r[0] for r in data["ERP.ERP_HR_POSITION"] if r[2] == "Салбарын захирал"}
        by_pos = defaultdict(list)
        for r in data["ERP.EMPLOYEE_HISTORY"]:
            if r[3] in pos and r[5] <= d:
                by_pos[r[3]].append((r[5], r[6]))
        gaps = []
        for rows in by_pos.values():
            rows.sort()
            for (s0, e0), (s1, _) in zip(rows, rows[1:]):
                if e0 is not None and s1 > e0 + dt.timedelta(days=1):
                    gaps.append((e0 + dt.timedelta(days=1), s1 - dt.timedelta(days=1)))
            last_end = rows[-1][1]
            if last_end is not None and last_end < d:
                gaps.append((last_end + dt.timedelta(days=1), d))
        days = [(min(g1, d) - g0).days + 1 for g0, g1 in gaps if start <= g0 <= d]
        return "BANK", {"BANK": _row(None, None, sum(days) / len(days) if days else 0)}
    raise KeyError(logic)
NPL = {"ХЭВИЙН БУС", "ЭРГЭЛЗЭЭТЭЙ", "МУУ"}


def own_rows(data, hr: HR, iid: str, start: dt.date, d: dt.date, params: dict, amap: dict) -> tuple[str, dict]:
    if iid in ("GL3003a", "IN2003"):
        report = iid
        pkeys = {int(x) for x in str(params.get("p_pkeys") or "").split(",") if x.strip()}
        users = {r[0] for r in data["COREMIS.GL_USER_BRANCH"]}
        sols = {r[0] for r in data["FINACLE.SOL"]}
        acc = defaultdict(lambda: [0.0, 0.0, 0])
        for r in data["COREMIS.GL_REPORT_DATA"]:
            txn, rep, ver, br, pkey, _, budget, run, bal = r
            if txn != d or rep != report or pkey not in pkeys or br not in sols:
                continue
            if report == "GL3003a" and br not in users:           # GL_USER_BRANCH-д бүртгэлгүй SOL хасагдана
                continue
            if report == "IN2003" and ver != "1":                  # ноорог (VERSION 2) хасагдана
                continue
            acc[str(br)][0] += bal
            acc[str(br)][1] += budget if report == "GL3003a" else run
            acc[str(br)][2] += 1
        return "SOL", {s: _row(a[0], a[1]) for s, a in acc.items()}
    if iid in ("loan_attention", "loan_npl", "loan_provision"):
        acc = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        for b in _loan_book(data, d):
            a = acc[b["sol"]]
            a[0] += b["out"]
            a[1] += b["out"] if b["cls"] == "ХУГАЦАА ХЭТЭРСЭН" else 0
            a[2] += b["out"] if b["cls"] in NPL else 0
            a[3] += b["prov"]
        if iid == "loan_attention":
            return "SOL", {s: _row(a[1], a[0]) for s, a in acc.items()}
        if iid == "loan_npl":
            return "SOL", {s: _row(a[2], a[0]) for s, a in acc.items()}
        return "SOL", {s: _row(a[3], a[2], a[3] / a[2] if a[2] else None) for s, a in acc.items()}
    if iid == "monitoring":
        acc = defaultdict(lambda: [0.0, 0])
        for r in data["COREMIS.LOAN_MONITORING_QA"]:
            if start <= r[2] <= d:
                acc[str(r[1])][0] += r[3] / 100
                acc[str(r[1])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if iid == "decision_speed":
        acc = defaultdict(lambda: [0, 0])
        for r in data["FINACLE.LOAN_APPLICATION"]:
            if r[5] is not None and start <= r[4] <= d:
                acc[str(r[2])][0] += (r[4] - r[3]).days
                acc[str(r[2])][1] += 1
        return "SOL", {s: _row(n, c) for s, (n, c) in acc.items()}
    if iid in ("digital_active", "active_customers"):
        cmg = {r[0]: (r[2], str(r[3])) for r in data["FINACLE.CMG"]}
        mon = {(r[0], r[1]): r for r in data["COREMIS.CUSTOMER_ACTIVITY_MONTHLY"]}
        months = [d]
        for _ in range(2):
            months.append(months[-1].replace(day=1) - dt.timedelta(days=1))
        cnt = defaultdict(int)
        for cif, (seg, sol) in cmg.items():
            cur = mon.get((d, cif))
            if seg != "CORP" or cur is None:
                continue
            if iid == "digital_active":
                ok = cur[2] >= 3 and cur[3] >= 2
            else:
                ok = "Y" in (cur[4], cur[5], cur[6], cur[7]) or all(
                    (m, cif) in mon and mon[(m, cif)][2] >= 3 for m in months)
            cnt[sol] += ok
        out = {}
        for r in data["COREMIS.CUSTOMER_PLAN"]:
            if r[0] == d and r[2] == "CORP":
                plan = r[4] if iid == "digital_active" else r[3]
                if plan is not None:
                    out[str(r[1])] = _row(cnt[str(r[1])], plan, cnt[str(r[1])] / plan if plan else None)
        return "SOL", out
    if iid in ("doc_check", "lc_check"):
        table = "COREMIS.DOC_ARCHIVE_CHECK" if iid == "doc_check" else "COREMIS.LOAN_COMMITTEE_CHECK"
        worst, cnt = {}, defaultdict(int)
        for r in data[table]:
            if start <= r[2] <= d and r[3] > 1:
                s = str(r[1])
                cnt[s] += 1
                if s not in worst or (r[3], r[2]) > worst[s][:2]:
                    worst[s] = (r[3], r[2], r[4])
        return "SOL", {str(r[0]): _row(None, None, cnt[str(r[0])], worst[str(r[0])][2] if str(r[0]) in worst
                                       else "Зөрчилгүй") for r in data["FINACLE.SOL"]}
    if iid == "jira_alarm":
        abh = {r[0]: r[2] or "(хоосон)" for r in data["JIRA.ABH_JIRA_NEW"]}
        units = defaultdict(set)
        for r in data["JIRA.JIRAISSUE_NEW"]:
            if r[2] == "11457" and start <= r[3] <= d:
                units[abh[r[0]]].add(r[1])
        return "UNIT", {u: _row(None, None, len(v)) for u, v in units.items()}
    if iid == "card_fraud":
        issue = {r[0]: str(r[2]) for r in data["CARDZONE.CARD"]}
        acc = defaultdict(lambda: [0, 0])
        for r in data["CARDZONE.CARD_TXN"]:
            if start <= r[3] <= d:
                acc[issue[r[1]]][0] += r[6] == "Y"
                acc[issue[r[1]]][1] += 1
        return "SOL", {s: _row(f, n) for s, (f, n) in acc.items()}
    if iid in ("bank_mgr_turnover", "bank_turnover"):
        k = 3 if iid == "bank_mgr_turnover" else 0
        f = hr.flow(start, d).values()
        hs, he, sp = (sum(x[k] for x in f), sum(x[k + 1] for x in f), sum(x[k + 2] for x in f))
        return "BANK", {"BANK": _row(sp, (hs + he) / 2)}
    if iid == "bank_appraisal":
        by_q = defaultdict(list)
        for r in data["ERP.ERP_HR_APPRAISAL"]:
            if start <= r[2] <= d:
                by_q[r[2]].append(r[3])
        avgs = [sum(v) / len(v) / 100 for v in by_q.values()]
        return "BANK", {"BANK": _row(sum(avgs) if avgs else None, len(avgs))}       # SQL: хоосон SUM = NULL
    if iid == "hr_ratio":
        hr_sols = sols_of(data, amap[40]["branch"], d)
        emp = hr.at(d)
        mgrs = sum(1 for h in emp if str(h["sol"]) in hr_sols and "МЕНЕЖЕР" in h["title"].upper())
        return "BANK", {"BANK": _row(len(emp), mgrs, len(emp) / mgrs if mgrs else None)}
    raise KeyError(iid)


SUM_RULE = {"complaints", "ethics", "doc_check", "lc_check", "jira_alarm"}
GRC_LOGIC = {"action_plan", "structure_change", "policy_age", "mb_review", "external_audit", "since_last_audit",
             "audit_rating", "high_risk_share", "follow_up", "remote_audit", "knowledge", "infosec", "director_vacancy"}


def activity_value(level: str, rows: dict, sols: set[str], rule_sum: bool, branch: str = "") -> dict:
    """Үйл ажиллагааны утга: SOL → өөрийн SOL-ууд, BANK/UNIT → бүх мөр."""
    if level == "SOL":
        chosen = {k: r for k, r in rows.items() if k in sols}
    elif level == "ACTIVITY":
        chosen = {k: r for k, r in rows.items() if k == str(branch)}          # энэ үйл ажиллагааны BRANCHID
    else:
        chosen = dict(rows)
    nums = [r["num"] for r in chosen.values() if r["num"] is not None]
    dens = [r["den"] for r in chosen.values() if r["den"] is not None]
    num = sum(nums) if nums else None
    den = sum(dens) if dens else None
    if rule_sum or den is None:
        vals = [r["value"] for r in chosen.values() if r["value"] is not None]
        value = sum(vals) if vals else None
    else:
        value = num / den if (num is not None and den) else None
    texts = sorted({r["text"] for r in chosen.values() if r["text"]})
    return {"num": num, "den": den, "value": value, "texts": texts, "rows": chosen}


# ── Оноо: мастерийн шатлалыг гараар уншсан босго ───────────────────────────────
def _lb(v, steps, else_):
    """steps = [(доод хил, оноо), ...] ихээс бага руу: v ≥ хил бол тэр оноо."""
    for bound, score in steps:
        if v >= bound:
            return score
    return else_


def _pct(f):
    return lambda v, texts: None if v is None else f(v * 100)


def _complaint(v, texts):
    if any("ДАГ" in t for t in texts):
        return 5
    if v is None or v == 0:
        return None                              # Үнэлэхгүй /Гомдол гараагүй/
    return 2 if v < 2 else 3 if v <= 3 else 4


def _text(mapping):
    def f(v, texts):
        hits = [mapping[t] for t in texts if t in mapping]
        return max(hits) if hits else None
    return f


CANON = {
    "5-84% ба түүнээс доош | 4-85%-89% | 3-90%-94% | 2-95%-99% | 1-100% ба түүнээс дээш":
        _pct(lambda p: _lb(p, [(100, 1), (95, 2), (90, 3), (85, 4)], 5)),
    "1-16 цагаас дээш | 2-14-15.9 цаг | 3-12-13.9 цаг | 4-10-11.9 цаг | 5-10 доош цаг":
        lambda v, t: None if v is None else _lb(v, [(16, 1), (14, 2), (12, 3), (10, 4)], 5),
    "0-Үнэлэхгүй | 1-1 | 2-95%-99% | 3-90%-94% | 4-85%-89% | 5-85%-с доош":
        _pct(lambda p: _lb(p, [(100, 1), (95, 2), (90, 3), (85, 4)], 5)),
    "0-Үнэлэхгүй | 1-1-2 жил | 2-2-3 жил | 3-3-4 жил | 4-4-5 жил | 5-0-1 жил and 5-с дээш жил":
        lambda v, t: None if v is None else 5 if v < 1 or v > 5 else _lb(v, [(4, 4), (3, 3), (2, 2)], 1),
    "0-Үнэлэхгүй | 1-1-2 жил | 2-2-3 жил | 3-3-3.5 жил | 4-3.5-4 жил | 5-0-1 жил and 4-с дээш жил/удирдлага "
    "байхгүй/Захирал нь өөр банкнаас томилогдсон.":
        lambda v, t: None if v is None else 5 if v < 1 or v > 4 else _lb(v, [(3.5, 4), (3, 3), (2, 2)], 1),
    "0-Үнэлэхгүй | 1-10%-аас бага | 2-10%-12% | 3-13%-15% | 4-16%-19% | 5-20% болон түүнээс дээш":
        _pct(lambda p: _lb(p, [(20, 5), (16, 4), (13, 3), (10, 2)], 1)),
    "0-Үнэлэхгүй /Үгүй/ | 5-Тийм": lambda v, t: None if not v else 5,
    "0-Үнэлэхгүй /Гомдол гараагүй/ | 2-ХҮГ-ын бүртгэлээр 2 хүртэл гомдол гарсан | 3-ХҮГ-ын бүртгэлээр 2-3 гомдол "
    "гарсан | 4-ХҮГ-ын бүртгэлээр 3-с дээш гомдол гарсан | 5-ДАГ-т гомдол ирж, шалгагдсан.": _complaint,
    "1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош": _pct(lambda p: _lb(p, [(96.1, 1), (90.1, 3)], 5)),
    "5-15-с дээш хувь | 4-13-14.9% | 3-11-12.9% | 2-9-10.9% | 1-9%-аас бага":
        _pct(lambda p: _lb(p, [(15, 5), (13, 4), (11, 3), (9, 2)], 1)),
    "1-2.5% ба түүнээс бага | 2-2.5%-3.9% | 3-4%-5.4% | 4-5.5%-6.9% | 5-7% ба түүнээс дээш":
        _pct(lambda p: 1 if p <= 2.5 else _lb(p, [(7, 5), (5.5, 4), (4, 3)], 2)),
    "5-5% түүнээс дээш | 4-0.05 | 3-4-4.9% | 2-3-3.9% | 1-3%-аас бага":        # "4-0.05" мастерт эвдэрсэн
        _pct(lambda p: _lb(p, [(5, 5), (4, 3), (3, 2)], 1)),
    "5-70% ба түүнээс доош | 4-71%-73% | 3-74%-77% | 2-77%-80% | 1-80% ба түүнээс дээш":
        _pct(lambda p: _lb(p, [(80, 1), (77, 2), (74, 3), (71, 4)], 5)),
    "5-0-59% | 4-60-69% | 3-70-79% | 2-80-89% | 1-90-100%":
        _pct(lambda p: _lb(p, [(90, 1), (80, 2), (70, 3), (60, 4)], 5)),
    "1-15 өдөрт | 2-16 өдөрт | 3-17 өдөрт | 4-18 өдөрт | 5-19-с дээш өдөрт. Судалгааны хурдыг хэмждэггүй.":
        lambda v, t: None if v is None else _lb(v, [(19, 5), (18, 4), (17, 3), (16, 2)], 1),
    " | ".join(f"{k}-{v}" for k, v in sorted(B.DOC_VIOLATIONS.items(), reverse=True)):
        _text({v: k for k, v in B.DOC_VIOLATIONS.items()}),
    " | ".join(f"{k}-{v}" for k, v in sorted(B.LC_VIOLATIONS.items(), reverse=True)):
        _text({v: k for k, v in B.LC_VIOLATIONS.items()}),
    "5-1:251-ээс дээш | 4-1:201-1:250 | 3-1:151-1:200 | 2-1:101-1:150 | 1-1:100 эсвэл түүнээс доош":
        lambda v, t: None if v is None else 1 if v <= 100 else 2 if v <= 150 else 3 if v <= 200 else 4 if v <= 250 else 5,
    "1-0.5%-аас бага | 2-0.5%-1% | 3-1%-2% | 4-2%-3% | 5-3%-аас дээш":
        _pct(lambda p: _lb(p, [(3, 5), (2, 4), (1, 3), (0.5, 2)], 1)),
    # ── master-т гарын, demo-д системээс тооцсон нийтлэг тодорхойлолт (хувилбаруудтай) ──
    "0-Үнэлэхгүй | 1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош": _pct(lambda p: _lb(p, [(96.1, 1), (90.1, 3)], 5)),
    "0-Үнэлэхгүй | 1-96.1%-аас дээш | 5-96%-с доош": _pct(lambda p: _lb(p, [(96.1, 1)], 5)),
    "0-Үнэлэхгүй | 1-96.1%-аас дээш | 2-92.1-96% | 3-89.1-92% | 4-85-89% | 5-85% - с доош":
        _pct(lambda p: _lb(p, [(96.1, 1), (92.1, 2), (89.1, 3), (85, 4)], 5)),
    "1-96.1%-аас дээш | 2-92.1%-96% | 3-89.1-92% | 4-85-89% | 5-85% - с доош":
        _pct(lambda p: _lb(p, [(96.1, 1), (92.1, 2), (89.1, 3), (85, 4)], 5)),
    "0-Үнэлэхгүй /Үгүй/ | 4-Алба | 5-Газар, хэлтэс": _text({"Алба": 4, "Газар, хэлтэс": 5}),
    "0-Үнэлэхгүй | 1-1 жил | 2-2 жил | 3-3 жил | 4-4 жил | 5-5 болон түүнээс дээш жил":
        lambda v, t: None if v is None else _lb(v, [(5, 5), (4, 4), (3, 3), (2, 2)], 1),
    "0-Үнэлэхгүй /МБ-ны шалгалт ороогүй / | 1-Сайн | 2-Хэвийн | 3-Дунд | 4-Хангалтгүй | 5-Муу":
        _text({"Сайн": 1, "Хэвийн": 2, "Дунд": 3, "Хангалтгүй": 4, "Муу": 5}),
    "0-Үнэлэхгүй /Хөндлөнгийн аудит/ | 1-Бага эрсдэлтэй зөвлөмж өгсөн /Зөвлөмж өгөөгүй | 3-Дунд эрсдэлтэй зөвлөмж өгсөн | "
    "5-Өндөр эрсдэлтэй зөвлөмж өгсөн": _text({"Бага эрсдэлтэй зөвлөмж өгсөн": 1, "Дунд эрсдэлтэй зөвлөмж өгсөн": 3,
                                              "Өндөр эрсдэлтэй зөвлөмж өгсөн": 5}),
    "0-Үнэлэхгүй /Хөндлөнгийн аудит/ | 1-Бага эрсдэлтэй зөвлөмж өгсөн /Зөвлөмж өгөөгүй | 3-Дунд эрсдэлтэй зөвлөмж өгсөн":
        _text({"Бага эрсдэлтэй зөвлөмж өгсөн": 1, "Дунд эрсдэлтэй зөвлөмж өгсөн": 3}),      # 5-гүй хувилбар
    "1-0-1 жил | 2-1-2 жил | 3-2-2.5 жил | 4-2.5-3 жил | 5-3 ба түүнээс дээш жил, аудит ороогүй":
        lambda v, t: 5 if "аудит ороогүй" in t else None if v is None else _lb(v, [(3, 5), (2.5, 4), (2, 3), (1, 2)], 1),
    "0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/ | 1-Хангалттай | 3-Сайжрулах шаардлагатай | 5-Хангалтгүй":
        _text({"Хангалттай": 1, "Сайжрулах шаардлагатай": 3, "Хангалтгүй": 5}),
    "0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/ | 1-Хангалттай | 3-Сайжруулах шаардлагатай | 5-Хангалтгүй":
        _text({"Хангалттай": 1, "Сайжрулах шаардлагатай": 3, "Хангалтгүй": 5}),   # SQL «Сайжрулах» ↔ үсгийн алдаа
    "0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/ | 1-Хангалттай | 3-Сайжрулах шаардлагатай":
        _text({"Хангалттай": 1, "Сайжрулах шаардлагатай": 3}),                  # 5-гүй хувилбар: Хангалтгүй → оноогүй
    "0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/ | 1-10% хүртэл | 2-10%-14% | 3-15%-20% | 4-21%-25% | 5-25%-иас дээш":
        _pct(lambda p: 5 if p > 25 else _lb(p, [(21, 4), (15, 3), (10, 2)], 1)),
    "0-Үнэлэхгүй /Өмнөх аудит хийж байгаагүй/ | 1-10% хүртэл | 2-10%-14% | 3-15%-20% | 4-21%-25% | 5-25%-иас дээш":
        _pct(lambda p: 5 if p > 25 else _lb(p, [(21, 4), (15, 3), (10, 2)], 1)),
    "0-Үнэлэхгүй | 1-95%-100% | 2-90%-94% | 3-85%-89% | 4-80%-84% | 5-80%-с доош":
        _pct(lambda p: _lb(p, [(95, 1), (90, 2), (85, 3), (80, 4)], 5)),
    "1-95%-100% | 2-90%-94% | 3-85%-89% | 4-80%-84% | 5-80%-с доош":
        _pct(lambda p: _lb(p, [(95, 1), (90, 2), (85, 3), (80, 4)], 5)),
    "1-90%-с дээш | 2-85-89% | 3-80-84% | 4-75-79% | 5-75-с доош":
        _pct(lambda p: _lb(p, [(90, 1), (85, 2), (80, 3), (75, 4)], 5)),
    "5-Зайны аудитаар зөрчил илэрч Илтгэх хуудас бичигдсэн | 4-Нэг төрлийн зөрчил давтагдан гарсан | 3-Нэг төрлийн "
    "зөрчил давтагдаагүй, өөр төрлийн зөрчил аудит дарааллан гарсан. | 2-Зайн аудитаар зөрчил гарсан боловч зөрчлийг "
    "арилгасан | 1-Зөрчил гараагүй.": _text({v: k for k, v in {
        5: "Зайны аудитаар зөрчил илэрч Илтгэх хуудас бичигдсэн", 4: "Нэг төрлийн зөрчил давтагдан гарсан",
        3: "Нэг төрлийн зөрчил давтагдаагүй, өөр төрлийн зөрчил аудит дарааллан гарсан",
        2: "Зайн аудитаар зөрчил гарсан боловч зөрчлийг арилгасан", 1: "Зөрчил гараагүй"}.items()}),
    "0-Үнэлэхгүй /Зөрчилгүй/ | 4-Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан | "
    "5-Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан зөрчил давтагдсан":
        _text({"Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан": 4,
               "Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан зөрчил давтагдсан": 5}),
    "0-Үнэлэхгүй /Зөрчилгүй/ | 4-Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш "
    "гаргасан | 5-Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш гаргасан зөрчил "
    "давтагдсан": _text({"Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш гаргасан": 4,
                         "Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш гаргасан "
                         "зөрчил давтагдсан": 5}),
    "1-5 хоног | 2-6 - 10 хоног | 3-11- 20 хоног | 4-21-30 хоног | 5-30 хоногоос дээш":
        lambda v, t: None if v is None else 5 if v > 30 else _lb(v, [(21, 4), (11, 3), (6, 2)], 1),
    "1-5 хоногоос доош. | 2-6 - 10 хоног | 3-11- 20 хоног | 4-21-30 хоног | 5-30 хоногоос дээш":
        lambda v, t: None if v is None else 5 if v > 30 else _lb(v, [(21, 4), (11, 3), (6, 2)], 1),
    "0-Үнэлэхгүй | 1-100% | 2-95%-99% | 3-90%-94% | 4-85%-89% | 5-85%-с доош":
        _pct(lambda p: _lb(p, [(100, 1), (95, 2), (90, 3), (85, 4)], 5)),
}


def scale_key(text: str) -> str:
    return " | ".join(ln.strip() for ln in str(text or "").strip().splitlines() if ln.strip())


def level(total, high=3.5, medium=2.5) -> str:
    if total is None:
        return ""
    return "Өндөр" if total >= high else "Дунд" if total >= medium else "Бага"


# ── Бүгд ──────────────────────────────────────────────────────────────────────
def expected(data, cat, dates) -> dict:
    """{(indicator_id, date): {...}} — автомат (sql / shared) үзүүлэлт бүр. Логик нь НЭРЭЭР (LOGIC), параметр нь
    тодорхойлолтын + үзүүлэлтийн params (жнь BI тайлангийн PKEY)."""
    import json
    from ri_runner.dedup import norm_key
    from ri_runner.runner import effective_params
    hr = HR(data)
    amap = activity_map()
    cache: dict = {}
    out = {}
    for d in dates:
        for ind in sorted(cat.indicators.values(), key=lambda i: i.indicator_id):
            if ind.mode == "manual" or not ind.enabled or ind.example:      # act_97 дадлага — verify-аар
                continue
            g = int(ind.activity_id[-2:])
            branch = amap[g]["branch"]
            la = last_audits(data, d).get(str(branch))              # GRC — config/local.yaml audit:
            audit = la[1] if la else None
            logic = LOGIC.get(norm_key(ind.name_mn))
            if logic is None:
                out[(ind.indicator_id, d)] = {"missing": True, "calc": norm_key(ind.name_mn)}
                continue
            params = effective_params(cat, ind)
            start = start_for(ind.period, d, audit)
            key = (logic, start, d, json.dumps(params, sort_keys=True, default=str))
            if key not in cache:
                cache[key] = calc_rows(data, hr, logic, start, d, params, amap)
            lvl, rows = cache[key]
            a = activity_value(lvl, rows, sols_of(data, branch, d), logic in SUM_RULE, str(branch))
            canon = CANON.get(scale_key(ind.scale_text))
            out[(ind.indicator_id, d)] = {"branch": branch, "start": start, "level": lvl, **a,
                                          "score": canon(a["value"], a["texts"]) if canon else None,
                                          "canon": canon is not None, "calc": logic}
    return out
