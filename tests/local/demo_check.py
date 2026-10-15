"""Стандарт банкны DEMO DB дээр БҮТЭН урсгал: 35 үйл ажиллагаа, 1,382 үзүүлэлт → ClickHouse → эталонтой тулгах.

    python tests/local/demo_check.py              # seed → run Q2, Q3 → гарын үнэлгээ → verify → эталон → тайлан
    python tests/local/demo_check.py --no-seed    # DB-г дахин ачаалахгүй (өмнөх seed хэвээр)

Алхам:
  1. seed_bank.py     Oracle (COREMIS, FINACLE, ERP, CARDZONE, JIRA) + ClickHouse cardzone_dwh, үр дүнгийн DB шинээр
  2. check            1,382 үзүүлэлтийн static шалгалт (--env local)
  3. run --all        303 автомат (9 нийтлэг тооцоолол × 35 үйл ажиллагаа + 20 өөрийн SQL) + 2 нэмэлт, Q2 ба Q3
  4. manual           гарын 1,077 үзүүлэлтийн template → жишээ утгаар бөглөж load (Excel-ээр)
  5. verify           source дээр дахин тооцоолж ClickHouse-тэй мөр бүрээр (бичихгүй)
  6. эталон           bank_golden.py (SQL-ээс үл хамааран Python) ↔ ClickHouse: утга, тоологч, хуваарь, SOL
                      задаргаа, оноо, sol_id, file_name, үйл ажиллагааны нийт оноо, түвшин
  7. тохиолдлууд      source-д бичих оролдлого хаагдах (Oracle, ClickHouse), дахин ажиллуулахад давхардахгүй
                      (ri_history), бүтцийн өөрчлөлт (2025-12-31 ↔ 2026-09-30 SOL), auto (устгасныг л нөхнө)
  8. алдааны тохиолдол түр activities/act_98_edge_cases/ (дуусахад устгана): timeout, procedure доторх UPDATE,
                      dependency тойрог, min_rows, source бэлэн биш, стандарт багана дутуу, давхардсан мөр —
                      алдаатай нь бусдыгаа зогсоохгүй, хуучин зөв үр дүн хэвээр үлдэнэ
Тайлан: output/demo_report.json, output/demo_report.html. Үр дүн risk_assessment_local-д үлдэнэ (DBeaver).
"""
import argparse
import datetime as dt
import html
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank_demo  # noqa: E402
import bank_golden as G  # noqa: E402
from ri_runner import orgmap  # noqa: E402
from ri_runner.config import EnvConfig  # noqa: E402
from ri_runner.db import RunnerError, classify_error, connect  # noqa: E402
from ri_runner.metadata import apply_env_params, load_catalog  # noqa: E402
from ri_runner.scale import UNELEHGUI, compute_score  # noqa: E402

ENV = "local"
PERIODS = {"2026-Q2": dt.date(2026, 6, 30), "2026-Q3": dt.date(2026, 9, 30)}
OUT_JSON, OUT_HTML = ROOT / "output" / "demo_report.json", ROOT / "output" / "demo_report.html"
GREEN, RED, YELLOW, CYAN, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[2m", "\033[1m", "\033[0m"


def ri(*args, timeout=900) -> tuple[int, str]:
    out = subprocess.run([sys.executable, "ri.py", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return out.returncode, out.stdout + out.stderr


def step(title: str) -> None:
    print(f"\n{BOLD}{CYAN}▶ {title}{OFF}")


def close(a, b, rel=1e-9) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=1e-9)


# ── Гарын үнэлгээ: template-ийг жишээ утгаар бөглөх ─────────────────────────────
def fill_manual(cat, d: dt.date, path: Path) -> dict:
    """Template-ийн мөр бүрийг тогтвортой санамсаргүй утгаар бөглөнө. {indicator_id: хүлээгдэх оноо|None}."""
    from openpyxl import load_workbook
    wb = load_workbook(path)
    ws = wb.active
    head = [c.value for c in ws[1]]
    col = {h: i + 1 for i, h in enumerate(head)}
    expected = {}
    for r in range(2, ws.max_row + 1):
        iid = ws.cell(r, col["INDICATOR_ID"]).value
        ind = cat.indicators[iid]
        rng = random.Random(f"{iid}|{d}")
        roll = rng.random()
        if roll < 0.08:                                   # бөглөөгүй — оноонд орохгүй
            expected[iid] = ("blank", None)
            continue
        if roll < 0.12:                                   # 0 = Үнэлэхгүй
            ws.cell(r, col["SCORE"]).value = 0
            expected[iid] = ("score", None)
            continue
        choice = _choose(ind, rng) if ind.scale and not ind.scale_error else None
        if choice is None:                                # шатлал задарсангүй → оноог гараар
            s = rng.randint(1, 5)
            ws.cell(r, col["SCORE"]).value = s
            ws.cell(r, col["COMMENT"]).value = "DEMO: шатлал задарсангүй — оноог гараар"
            expected[iid] = ("score", float(s))
            continue
        kind, val, score = choice
        ws.cell(r, col["VALUE" if kind == "value" else "VALUE_TEXT"]).value = val
        ws.cell(r, col["COMMENT"]).value = "DEMO утга"
        expected[iid] = (kind, float(score))
    wb.save(path)
    return expected


def _choose(ind, rng):
    """Шатлалын 1–5 онооны нэг мөрийг сонгож, түүнд яг тохирох утга (тоо эсвэл ангиллын текст)."""
    sc = ind.scale
    opts = []
    for rule in sc.get("numericRules") or []:
        if rule["score"] in (1, 2, 3, 4, 5):
            lo, hi = rule.get("min"), rule.get("max")
            if lo is None and hi is None:
                continue
            v = (lo + hi) / 2 if lo is not None and hi is not None else (hi - 1 if lo is None else lo + 1)
            if sc.get("unit") == "percent":
                v = round(v / 100, 6)
            opts.append(("value", v, rule["score"]))
    for rule in sc.get("stringRules") or []:
        if rule["score"] in (1, 2, 3, 4, 5) and rule.get("values"):
            opts.append(("text", rule["values"][0], rule["score"]))
    rng.shuffle(opts)
    for kind, v, score in opts:                       # давхцсан (эвдэрсэн) мөрийг алгасна
        got, _ = compute_score(sc, v, value_unit=ind.value_unit)
        if got == score:
            return kind, v, score
    return None


# ── ClickHouse-оос унших ──────────────────────────────────────────────────────
def read_results(cfg) -> tuple[dict, dict, dict]:
    with connect(cfg, cfg.result_connection) as ch:
        cols = ["row_type", "report_date", "indicator_id", "activity_id", "branch_id", "sol_id", "file_name",
                "source_kind", "entity_level", "entity_id", "metric", "numerator", "denominator", "value",
                "value_text", "score", "weight", "level", "n_scored", "n_indicators", "weight_coverage",
                "period_start", "run_id"]
        _, rows = ch.query(f"SELECT {', '.join(cols)} FROM `{cfg.result_db}`.ri_result "
                           f"WHERE report_date IN {{d:Array(Date)}}", {"d": list(PERIODS.values())})
    ind_rows, drill, acts = {}, defaultdict(dict), {}
    for r in rows:
        x = dict(zip(cols, r))
        d = x["report_date"]
        if x["row_type"] == "ACTIVITY":
            acts[(x["branch_id"], d)] = x
        elif x["entity_level"] == "ACTIVITY":
            ind_rows.setdefault((x["indicator_id"], d), {})[x["metric"]] = x
        else:
            drill[(x["indicator_id"], d)][x["entity_id"]] = x
    return ind_rows, drill, acts


# ── Тохиолдлууд (хамгаалалт, дахин ажиллуулах, бүтэц, auto) ─────────────────────
def guard_cases(cfg) -> list[dict]:
    out = []
    for name, conn_name, sql in (
            ("Oracle source-д бичих оролдлого", "oracle_whouse",
             "UPDATE ERP.ERP_EMPLOYEE SET END_DATE = NULL WHERE EMPLOYEE_ID = 1"),
            ("ClickHouse source-д бичих оролдлого", "clickhouse_dwh",
             "INSERT INTO cardzone_dwh.card_txn (txn_id) VALUES (999999999)")):
        try:
            with connect(cfg, conn_name, read_only=True) as c:
                c.query(sql, {})
            out.append({"case": name, "ok": False, "detail": "бичих боломжтой байна!"})
        except Exception as exc:  # noqa: BLE001
            code, msg = classify_error(exc)
            out.append({"case": name, "ok": code == "SOURCE_WRITE_BLOCKED", "detail": f"{code}: {msg[:120]}"})
    return out


EDGE_DIR = ROOT / "activities" / "act_98_edge_cases"
EDGE_BRANCH = "9098"
EDGE_HEAD = """/*---
indicator_id: {iid}
name_mn: "{name}"
status: IN_PROGRESS
version: 0.1.0
connection: oracle_whouse
frequency: quarterly
{extra}---*/
"""
BANK_SQL = ("SELECT 'BANK' AS ENTITY_LEVEL, 'BANK' AS ENTITY_ID, COUNT(*) AS VALUE "
            "FROM {{schema.erp}}.ERP_EMPLOYEE e WHERE e.HIRE_DATE <= :p_report_date")
# (ID, нэр, тохиргоо, SQL, хүлээгдэх төлөв, алдааны код)
EDGE = [
    ("RI_98_9001", "Timeout (3 сек унтаж, хязгаар 1 сек)", "timeout_seconds: 1\n",
     "BEGIN\n  DBMS_SESSION.SLEEP(3);\n  OPEN :rc FOR " + BANK_SQL + ";\nEND;", "TIMEOUT", "TIMEOUT"),
    ("RI_98_9002", "Procedure дотор source-д бичих оролдлого", "",
     "BEGIN\n  UPDATE {{schema.erp}}.ERP_EMPLOYEE SET END_DATE = END_DATE WHERE 1 = 0;\n  OPEN :rc FOR "
     + BANK_SQL + ";\nEND;", "FAILED", "SOURCE_WRITE_BLOCKED"),
    ("RI_98_9003", "Dependency тойрог A", "dependencies: [RI_98_9004]\n", BANK_SQL, "SKIPPED", "DEPENDENCY_CYCLE"),
    ("RI_98_9004", "Dependency тойрог B", "dependencies: [RI_98_9003]\n", BANK_SQL.replace("COUNT(*)", "COUNT(e.EMPLOYEE_ID)"),
     "SKIPPED", "DEPENDENCY_CYCLE"),
    ("RI_98_9005", "min_rows: 1000 (source дутуу)", "min_rows: 1000\n", BANK_SQL.replace("COUNT(*)", "COUNT(1)"),
     "VALIDATION_FAILED", "VALIDATION_FAILED"),
    ("RI_98_9006", "Source бэлэн биш (source_check = 0)",
     "source_check: |\n  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA WHERE TXNDATE = :p_report_date + 1\n",
     BANK_SQL.replace("COUNT(*)", "COUNT(e.HIRE_DATE)"), "SKIPPED", "SOURCE_NOT_READY"),
    ("RI_98_9007", "Стандарт багана VALUE алга", "",
     "SELECT 'BANK' AS ENTITY_LEVEL, 'BANK' AS ENTITY_ID, COUNT(*) AS CNT FROM {{schema.erp}}.ERP_EMPLOYEE e "
     "WHERE e.HIRE_DATE <= :p_report_date", "FAILED", "OUTPUT_SCHEMA"),
    ("RI_98_9008", "Давхардсан мөр (BANK × 2)", "",
     "SELECT 'BANK' AS ENTITY_LEVEL, 'BANK' AS ENTITY_ID, 1 AS VALUE FROM {{schema.erp}}.HR_ORG_DEPARTMENT d "
     "WHERE d.OPEN_DATE <= :p_report_date AND ROWNUM <= 2", "VALIDATION_FAILED", "VALIDATION_FAILED"),
    ("RI_98_9009", "Хэвийн (бусад алдаа үүнийг зогсоохгүй)", "", BANK_SQL.replace("COUNT(*)", "COUNT(e.GENDER)"),
     "SUCCESS", ""),
    ("RI_98_9010", "Dependency нь timeout болсон", "dependencies: [RI_98_9001]\n",
     BANK_SQL.replace("COUNT(*)", "COUNT(e.BIRTH_DATE)"), "SKIPPED", "DEPENDENCY_FAILED"),
]


def edge_cases(cfg) -> list[dict]:
    """Түр activity-д алдааны төрөл бүрийг үүсгэж ажиллуулаад audit-ийн төлөв, кодыг шалгана. Дуусахад устгана."""
    import shutil
    out = []
    try:
        EDGE_DIR.mkdir(exist_ok=True)
        (EDGE_DIR / "activity.yaml").write_text(
            f"activity_id: ACT_98\nactivity_name_mn: \"Алдааны тохиолдол (demo_check, түр)\"\n"
            f"activity_name_en: Edge cases\nbranch_id: \"{EDGE_BRANCH}\"\nexample: true\nowner: demo\nreviewer: demo\n",
            encoding="utf-8")
        for iid, name, extra, sql, _, _ in EDGE:
            (EDGE_DIR / f"{iid.lower()}.sql").write_text(EDGE_HEAD.format(iid=iid, name=name, extra=extra) + sql + "\n",
                                                        encoding="utf-8")
        rc, log = ri("run", "--env", ENV, str(EDGE_DIR.relative_to(ROOT)), "-d", "2026-09-30")
        run_id = next((ln.split("RUN ", 1)[1].split()[0] for ln in log.splitlines() if ln.startswith("RUN ")), "")
        with connect(cfg, cfg.result_connection) as ch:
            _, rows = ch.query(f"SELECT indicator_id, argMax(execution_status, finished_at), argMax(error_code, finished_at), "
                               f"argMax(error_message, finished_at) FROM `{cfg.result_db}`.ri_execution_audit "
                               f"WHERE run_id = {{r:String}} GROUP BY indicator_id", {"r": run_id})
        got = {r[0]: (r[1], r[2] or "", r[3] or "") for r in rows}
        for iid, name, _, _, status, code in EDGE:
            st, cd, msg = got.get(iid, ("алга", "", ""))
            out.append({"case": f"{iid} {name}", "ok": st == status and cd == code,
                        "detail": f"хүлээгдэх {status} {code} → {st} {cd} {msg[:90]}".strip()})
        out.append({"case": "Алдаатай run-ий exit code", "ok": rc == 1, "detail": f"rc={rc} (алдаатай бол 1)"})
    finally:                                       # үр дүн (ACTIVITY мөр ч), audit-ийг устгаад folder-ийг
        if EDGE_DIR.exists():
            ri("clean", "--env", ENV, "-a", "ACT_98", *sum((["-i", e[0]] for e in EDGE), []), "--audit", "--yes")
        shutil.rmtree(EDGE_DIR, ignore_errors=True)
    return out


def scalar(cfg, sql, params=None):
    with connect(cfg, cfg.result_connection) as ch:
        _, rows = ch.query(sql, params or {})
    return rows[0][0] if rows else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-seed", action="store_true", help="Demo DB-г дахин ачаалахгүй")
    args = ap.parse_args()
    t0 = time.time()
    cfg = EnvConfig(ENV)
    rep: dict = {"started": dt.datetime.now().isoformat(timespec="seconds"), "steps": [], "cases": []}

    def log_step(name, rc, seconds, note=""):
        rep["steps"].append({"step": name, "rc": rc, "seconds": round(seconds, 1), "note": note})
        mark = f"{GREEN}✔{OFF}" if rc == 0 else f"{RED}✘{OFF}"
        print(f"  {mark} {name} ({seconds:.1f}s) {note}")

    if not args.no_seed:
        step("1. Demo DB (seed_bank.py) + үр дүнгийн DB шинээр")
        s = time.time()
        p = subprocess.run([sys.executable, "tests/local/seed_bank.py"], cwd=ROOT, capture_output=True, text=True)
        print("\n".join("   " + ln for ln in p.stdout.splitlines()[-4:]))
        with connect(cfg, cfg.result_connection) as ch:
            ch.execute(f"DROP DATABASE IF EXISTS `{cfg.result_db}` SYNC")
        rc, _ = ri("init-db", "--env", ENV)
        log_step("seed + init-db", p.returncode or rc, time.time() - s)
        if p.returncode or rc:
            print(p.stderr[-2000:])
            return 1

    orgmap.use(cfg)
    cat = load_catalog()
    apply_env_params(cat, cfg)
    data = bank_demo.build()

    step("2. Static шалгалт (ri.py check --env local)")
    s = time.time()
    rc, out = ri("check", "--env", ENV)
    log_step("check", rc, time.time() - s, out.strip().splitlines()[-1])

    step("3. Автомат үзүүлэлтүүд: run --all -p 2026-Q2 -p 2026-Q3")
    s = time.time()
    rc, out = ri("run", "--env", ENV, "--all", *sum((["-p", p] for p in PERIODS), []))
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "output" / "demo_run.log").write_text(out, encoding="utf-8")
    summary = [ln for ln in out.splitlines() if ln.startswith("TOTAL")]
    log_step("run", rc, time.time() - s, summary[0] if summary else "")

    step("4. Гарын үнэлгээ: manual template → жишээ утга → load")
    manual_expected = {}
    s = time.time()
    for per, d in PERIODS.items():
        rc, out = ri("manual", "template", "--date", d.isoformat())
        path = Path(out.split("Үүсгэлээ:", 1)[1].split("\n", 1)[0].strip())
        manual_expected[d] = fill_manual(cat, d, path)
        rc, out = ri("manual", "load", str(path), "--env", ENV)
        n = sum(1 for k, v in manual_expected[d].items() if v[0] != "blank")
        log_step(f"manual {per}", rc, time.time() - s, f"{n} мөр ({path.name})")
        if rc:
            print(out[-3000:])
        s = time.time()

    step("5. verify --all (source дээр дахин тооцоолж ClickHouse-тэй, бичихгүй)")
    s = time.time()
    rc, out = ri("verify", "--env", ENV, "--all", *sum((["-p", p] for p in PERIODS), []))
    (ROOT / "output" / "demo_verify.log").write_text(out, encoding="utf-8")
    last = [ln for ln in out.splitlines() if ln.startswith("VERIFY:")]
    log_step("verify", rc, time.time() - s, last[0] if last else out[-300:])
    rep["verify_rc"] = rc

    step("6. Эталон (bank_golden.py) ↔ ClickHouse")
    gold = G.expected(data, cat, list(PERIODS.values()))
    ind_rows, drill, acts = read_results(cfg)
    checks = []                                   # {indicator, date, ok, kind, detail}
    master = []                                   # мастерийн шатлалын асуудал
    scores_used: dict = {}
    for (iid, d), g in sorted(gold.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        ind = cat.indicators[iid]
        if g.get("missing"):                       # эталонд логик алга — шинэ SQL нэмсэн бол bank_golden.LOGIC-д
            checks.append({"indicator": iid, "date": str(d), "ok": False, "kind": ind.mode,
                           "detail": f"эталон алга: bank_golden.LOGIC-д '{g['calc']}' нэмнэ"})
            continue
        got = (ind_rows.get((iid, d)) or {}).get(ind.score_metric)
        prob = []
        if got is None:
            if g["value"] is None and not g["rows"]:
                checks.append({"indicator": iid, "date": str(d), "ok": True, "kind": "empty",
                               "detail": "source 0 мөр — бичигдээгүй (зөв)"})
                continue
            prob.append("ClickHouse-д мөр алга")
        else:
            for f, gv in (("value", g["value"]), ("numerator", g["num"]), ("denominator", g["den"])):
                if not close(got[f], gv):
                    prob.append(f"{f}: эталон={gv} ClickHouse={got[f]}")
            if str(got["branch_id"]) != str(g["branch"]):
                prob.append(f"branch_id {got['branch_id']} ≠ {g['branch']}")
            want_sols = ",".join(sorted(G.sols_of(data, g["branch"], d), key=lambda x: (len(x), x)))
            if got["sol_id"] != want_sols:
                prob.append(f"sol_id '{got['sol_id']}' ≠ '{want_sols}'")
            if got["file_name"] != ind.file_name:
                prob.append(f"file_name {got['file_name']} ≠ {ind.file_name}")
            if got["period_start"] != g["start"]:
                prob.append(f"period_start {got['period_start']} ≠ {g['start']}")
            want_drill = dict(g["rows"]) if g["level"] not in ("BANK", "ACTIVITY") else {}     # задаргаа: SOL, UNIT
            have = drill.get((iid, d), {})
            if set(have) != set(want_drill):
                prob.append(f"задаргаа: эталон {len(want_drill)} мөр, ClickHouse {len(have)} "
                            f"(илүү {sorted(set(have) - set(want_drill))[:3]}, дутуу {sorted(set(want_drill) - set(have))[:3]})")
            else:
                bad = [k for k, r in want_drill.items() if not (close(have[k]["value"], r["value"])
                       and close(have[k]["numerator"], r["num"]) and close(have[k]["denominator"], r["den"]))]
                if bad:
                    prob.append(f"задаргааны {len(bad)} мөр зөрүүтэй: {bad[:3]}")
            # Оноо: мастерийн шатлалыг гараар уншсан босготой
            if g["canon"]:
                if not close(got["score"], g["score"]):
                    prob.append(f"оноо: эталон={g['score']} ClickHouse={got['score']} (value={g['value']})")
            elif ind.weight:
                master.append({"indicator": iid, "date": str(d), "score": got["score"],
                               "scale": G.scale_key(ind.scale_text)[:160], "calc": g["calc"]})
            scores_used[(iid, d)] = got["score"]
        checks.append({"indicator": iid, "date": str(d), "ok": not prob, "kind": ind.mode,
                       "value": g["value"], "score": g["score"] if g["canon"] else (got or {}).get("score"),
                       "detail": "; ".join(prob)})
    # Гарын үнэлгээ: оноо
    for d, exp in manual_expected.items():
        for iid, (kind, score) in sorted(exp.items()):
            got = (ind_rows.get((iid, d)) or {}).get(cat.indicators[iid].score_metric)
            if kind == "blank":
                ok = got is None
                detail = "" if ok else "бөглөөгүй мөр ClickHouse-д байна"
            else:
                ok = got is not None and close(got["score"], score) and got["source_kind"] == "MANUAL"
                detail = "" if ok else f"оноо: хүлээгдэх={score} ClickHouse={None if got is None else got['score']}"
                scores_used[(iid, d)] = score
            checks.append({"indicator": iid, "date": str(d), "ok": ok, "kind": "manual", "score": score,
                           "detail": detail})
    # Үйл ажиллагааны нийт оноо: эталон оноонуудаас
    act_rows = []
    amap = G.activity_map()
    for d in PERIODS.values():
        for aid, act in sorted(cat.activities.items()):
            if act.example:
                continue
            branch = amap[act.group_no]["branch"]
            inds = [i for i in cat.by_activity(aid) if i.enabled]
            pairs = [(scores_used.get((i.indicator_id, d)), i.weight) for i in inds if i.weight]
            sc = [(s, w) for s, w in pairs if s is not None and s > 0]
            sw = sum(w for _, w in sc)
            total = sum(s * w for s, w in sc) / sw if sw else None
            got = acts.get((branch, d))
            ok = got is not None and close(got["value"], total) and (got["level"] or "") == G.level(total) \
                and int(got["n_scored"] or 0) == len(sc)
            act_rows.append({"activity": aid, "group": act.group_no, "name": act.name_mn, "branch": branch,
                             "date": str(d), "total": total, "level": G.level(total), "n_scored": len(sc),
                             "n": len(inds), "weight": sum(w for _, w in pairs if w),
                             "coverage": sw / sum(w for _, w in pairs if w) if pairs else None,
                             "ch_total": None if got is None else got["value"],
                             "ch_level": None if got is None else got["level"], "ok": ok,
                             "sols": ",".join(sorted(G.sols_of(data, branch, d), key=lambda x: (len(x), x)))})
    n_ok = sum(c["ok"] for c in checks)
    n_act_ok = sum(a["ok"] for a in act_rows)
    print(f"  үзүүлэлт × өдөр: {GREEN}{n_ok}{OFF} / {len(checks)} таарсан"
          + ("" if n_ok == len(checks) else f", {RED}{len(checks) - n_ok} зөрүүтэй{OFF}"))
    print(f"  үйл ажиллагааны нийт оноо: {GREEN}{n_act_ok}{OFF} / {len(act_rows)} таарсан")
    for c in [c for c in checks if not c["ok"]][:25]:
        print(f"    {RED}✘{OFF} {c['indicator']} {c['date']} {c['detail'][:200]}")
    for a in [a for a in act_rows if not a["ok"]][:10]:
        print(f"    {RED}✘{OFF} {a['activity']} {a['date']} эталон {a['total']} {a['level']} ({a['n_scored']}) ↔ "
              f"ClickHouse {a['ch_total']} {a['ch_level']}")
    if master:
        print(f"  {YELLOW}МАСТЕР{OFF}: стандарт бус шатлалтай {len({m['indicator'] for m in master})} автомат үзүүлэлт "
              f"(оноо нь мастерийн бичиглэлээр) — тайланд")

    step("7. Тохиолдлууд")
    cases = guard_cases(cfg)
    # Дахин ажиллуулахад давхардахгүй, хуучин нь ri_history-д
    before = scalar(cfg, f"SELECT count() FROM `{cfg.result_db}`.ri_result WHERE branch_id = '1006' "
                         f"AND report_date = '2026-09-30'")
    hist0 = scalar(cfg, f"SELECT count() FROM `{cfg.result_db}`.ri_history")
    rc, _ = ri("run", "--env", ENV, "activities/act_40_human_resources/", "-p", "2026-Q3")
    after = scalar(cfg, f"SELECT count() FROM `{cfg.result_db}`.ri_result WHERE branch_id = '1006' "
                        f"AND report_date = '2026-09-30'")
    hist1 = scalar(cfg, f"SELECT count() FROM `{cfg.result_db}`.ri_history")
    cases.append({"case": "act_40-ийг дахин ажиллуулахад давхардахгүй", "ok": rc == 0 and before == after and hist1 > hist0,
                  "detail": f"ri_result {before} → {after} мөр, ri_history +{hist1 - hist0}"})
    # Бүгдийг (305 × Q3, 4 thread зэрэг) дахин ажиллуулахад нэг ч түлхүүр давхардахгүй (DELETE баталгаа)
    s0 = time.time()
    rc, out = ri("run", "--env", ENV, "--all", "-p", "2026-Q3")
    dups = scalar(cfg, f"SELECT count() FROM (SELECT 1 FROM `{cfg.result_db}`.ri_result WHERE report_date IN "
                       f"('2026-06-30', '2026-09-30') GROUP BY row_type, report_date, indicator_id, branch_id, "
                       f"entity_level, entity_id, metric HAVING count() > 1)")
    retried = out.count("DELETE-ийн дараа")
    cases.append({"case": "--all-ийг дахин ажиллуулахад давхардсан мөр 0", "ok": rc == 0 and dups == 0,
                  "detail": f"давхардсан түлхүүр {dups}, DELETE дахин оролдлого {retried}, {time.time() - s0:.0f}s"})
    # Бүтцийн өөрчлөлт: 2025-12-31 (snapshot 2026-01-01: 819) ↔ 2026-09-30 (818)
    rc, _ = ri("run", "--env", ENV, "-i", "RI_01_0027", "-d", "2025-12-31")
    old = scalar(cfg, f"SELECT any(sol_id) FROM `{cfg.result_db}`.ri_result WHERE indicator_id = 'RI_01_0027' "
                      f"AND report_date = '2025-12-31' AND entity_level = 'ACTIVITY'") or ""
    new = scalar(cfg, f"SELECT any(sol_id) FROM `{cfg.result_db}`.ri_result WHERE indicator_id = 'RI_01_0027' "
                      f"AND report_date = '2026-09-30' AND entity_level = 'ACTIVITY'") or ""
    cases.append({"case": "Бүтцийн өөрчлөлт (MAIN snapshot) автоматаар", "ok": rc == 0 and "819" in old.split(",")
                  and "818" not in old.split(",") and "818" in new.split(",") and "819" not in new.split(","),
                  "detail": f"2025-12-31: {old}  →  2026-09-30: {new}"})
    # auto: бүгд шинэчлэгдсэн → 0; нэг үзүүлэлтийн мөрийг устгавал зөвхөн түүнийг
    rc0, out0 = ri("auto", "--env", ENV, "--all", "--plan", "--as-of", "2026-10-14", "--since", "2026-06-30")
    ri("clean", "--env", ENV, "-i", "RI_40_1545", "-d", "2026-09-30", "--audit", "--yes")
    rc1, out1 = ri("auto", "--env", ENV, "--all", "--plan", "--as-of", "2026-10-14", "--since", "2026-06-30")
    rc2, out2 = ri("auto", "--env", ENV, "--all", "--as-of", "2026-10-14", "--since", "2026-06-30")
    rc3, out3 = ri("auto", "--env", ENV, "--all", "--plan", "--as-of", "2026-10-14", "--since", "2026-06-30")
    first = lambda o: next((ln for ln in o.splitlines() if ln.startswith("AUTO")), o[-200:])  # noqa: E731
    cases.append({"case": "auto: дутууг л нөхнө (idempotent)",
                  "ok": "ажиллуулах зүйл алга" in out0 and "ШИНЭ 1" in out1 and rc2 == 0
                  and "ажиллуулах зүйл алга" in out3,
                  "detail": f"{first(out0)} | устгасны дараа: {first(out1)} | дахин: {first(out3)}"})
    rc, out = ri("verify", "--env", ENV, "activities/act_40_human_resources/", "-p", "2026-Q3")
    cases.append({"case": "verify (act_40, давтан ажиллуулсны дараа)", "ok": rc == 0,
                  "detail": next((ln for ln in out.splitlines() if ln.startswith("VERIFY:")), "")})
    rc, out = ri("run", "--env", ENV, "activities/act_97_practice/", "-p", "2026-Q3")
    rc2, out2 = ri("verify", "--env", ENV, "activities/act_97_practice/", "-p", "2026-Q3")
    cases.append({"case": "Дадлагын folder (act_97: Oracle, CARDZONE, ri_result-аас dependency)",
                  "ok": rc == 0 and rc2 == 0,
                  "detail": next((ln for ln in out2.splitlines() if ln.startswith("VERIFY:")), out[-200:])})
    step("8. Алдааны тохиолдлууд (түр activities/act_98_edge_cases/)")
    edge = edge_cases(cfg)
    for c in edge:
        print(f"  {GREEN + '✔' if c['ok'] else RED + '✘'}{OFF} {c['case']}: {c['detail'][:150]}")
    cases += edge
    rc, out = ri("verify", "--env", ENV, "--all", "-p", "2026-Q3")
    cases.append({"case": "Алдааны тохиолдлын дараа бүх үр дүн хэвээр (verify --all Q3)", "ok": rc == 0,
                  "detail": next((ln for ln in out.splitlines() if ln.startswith("VERIFY:")), "")})
    for c in [c for c in cases if c not in edge]:
        print(f"  {GREEN + '✔' if c['ok'] else RED + '✘'}{OFF} {c['case']}: {c['detail'][:180]}")
    rep["cases"] = cases

    # ── Тодорхойлолт бүрээр (давхардалгүй 498): эталон / гарын тулгалт ──
    per_def: dict = {}
    for c in checks:
        ind = cat.indicators[c["indicator"]]
        did = ind.calc_id
        e = per_def.setdefault(did, {"def": did, "name": (cat.calcs.get(did) or ind).name_mn, "mode": ind.mode,
                                     "common": did in cat.calcs, "acts": set(), "ok": 0, "n": 0})
        e["acts"].add(ind.activity_id)
        e["n"] += 1
        e["ok"] += c["ok"]
    definitions = sorted(({**e, "acts": len(e["acts"])} for e in per_def.values()),
                         key=lambda e: (not e["common"], e["mode"] == "manual", -e["acts"], e["def"]))
    n_def_ok = sum(e["ok"] == e["n"] for e in definitions)
    print(f"  тодорхойлолт бүрээр: {n_def_ok} / {len(definitions)} бүх хуулбартаа таарсан "
          f"(нийтлэг {sum(e['common'] for e in definitions)}, автомат {sum(e['mode'] != 'manual' for e in definitions)})")

    # ── Тайлан ──
    by_kind = Counter((c["kind"], c["ok"]) for c in checks)
    rep.update({
        "finished": dt.datetime.now().isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
        "checks": checks, "activities": act_rows, "master": master, "definitions": definitions,
        "summary": {"checks": len(checks), "ok": n_ok, "acts": len(act_rows), "acts_ok": n_act_ok,
                    "by_kind": {f"{k}|{ok}": n for (k, ok), n in by_kind.items()},
                    "cases": len(cases), "cases_ok": sum(c["ok"] for c in cases)},
        "db": {k: len(v) for k, v in data.items() if not k.startswith("_")},
        "examples": examples(cat, gold, drill),
    })
    OUT_JSON.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    OUT_HTML.write_text(render(rep), encoding="utf-8")
    all_ok = (n_ok == len(checks) and n_act_ok == len(act_rows) and all(c["ok"] for c in cases)
              and rep["verify_rc"] == 0 and n_def_ok == len(definitions))
    print(f"\n{BOLD}{GREEN + 'АМЖИЛТТАЙ' if all_ok else RED + 'ЗӨРҮҮТЭЙ'}{OFF}{BOLD}: эталон {n_ok}/{len(checks)}, "
          f"нийт оноо {n_act_ok}/{len(act_rows)}, тохиолдол {rep['summary']['cases_ok']}/{len(cases)}, "
          f"verify rc={rep['verify_rc']}  ({rep['seconds']}s){OFF}")
    print(f"Тайлан: {OUT_HTML.relative_to(ROOT)}")
    return 0 if all_ok else 1


def examples(cat, gold, drill) -> list[dict]:
    """Тайланд: act_01, act_40-ийн автомат үзүүлэлт бүр (Q3) — утга, оноо, SOL задаргаа."""
    d = PERIODS["2026-Q3"]
    out = []
    for (iid, dd), g in sorted(gold.items()):
        if dd != d or not (iid.startswith("RI_01_") or iid.startswith("RI_40_")):
            continue
        ind = cat.indicators[iid]
        out.append({"indicator": iid, "name": ind.name_mn, "mode": ind.mode, "calc": ind.calc or "",
                    "period": ind.period, "start": str(g["start"]), "num": g["num"], "den": g["den"],
                    "value": g["value"], "texts": g["texts"], "score": g["score"], "unit": (ind.scale or {}).get("unit"),
                    "weight": ind.weight, "level": g["level"],
                    "sols": [{"sol": k, "num": r["num"], "den": r["den"], "value": r["value"], "text": r["text"]}
                             for k, r in sorted(g["rows"].items())][:12]})
    return out


# ── HTML ──────────────────────────────────────────────────────────────────────
def _e(v) -> str:
    return html.escape("" if v is None else str(v))


def _n(v, unit=None, digits=4) -> str:
    if v is None:
        return "—"
    if unit == "percent":
        return f"{v * 100:.2f}%"
    if isinstance(v, float):
        return f"{v:,.{digits}g}" if abs(v) < 1e6 else f"{v:,.0f}"
    return f"{v:,}" if isinstance(v, int) else _e(v)


CSS = """
/* Хяналтын самбар: хураангуй → үйл ажиллагааны онооны шкал (1–5, босго 2.5 / 3.5) → тулгалт → тохиолдол */
:root{--bg:#f4f6f5;--card:#ffffff;--ink:#16211e;--mute:#5d6b67;--line:#dde3e0;--acc:#0f6b5c;
--ok:#1d7a4a;--okbg:#e3f3ea;--bad:#b3261e;--badbg:#fbe9e7;--hi:#c0392b;--mid:#c27c0e;--lo:#2e8b57;--track:#e7ecea;
--f-display:"Onest","IBM Plex Sans",system-ui,sans-serif;--f-body:"IBM Plex Sans",system-ui,-apple-system,sans-serif;
--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1513;--card:#161e1b;--ink:#e6ece9;
--mute:#93a29d;--line:#26302c;--acc:#5cc3ad;--ok:#6fd39e;--okbg:#173327;--bad:#ff8a80;--badbg:#3a1d1b;--hi:#ff7b6b;
--mid:#f0b45a;--lo:#6fd39e;--track:#222c28;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1513;--card:#161e1b;--ink:#e6ece9;--mute:#93a29d;--line:#26302c;--acc:#5cc3ad;
--ok:#6fd39e;--okbg:#173327;--bad:#ff8a80;--badbg:#3a1d1b;--hi:#ff7b6b;--mid:#f0b45a;--lo:#6fd39e;--track:#222c28;
color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 var(--f-body)}
main{max-width:1180px;margin:0 auto;padding:28px 16px 64px;display:grid;gap:14px}main>*{min-width:0}
h1{font:600 26px/1.2 var(--f-display);margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font:600 17px/1.3 var(--f-display);margin:22px 0 0;text-wrap:balance}
p.lead{color:var(--mute);margin:0;max-width:78ch}.eyebrow{font:600 11px/1 var(--f-body);letter-spacing:.08em;
text-transform:uppercase;color:var(--acc)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;display:grid;gap:2px}
.card b{font:600 24px/1.2 var(--f-mono);font-variant-numeric:tabular-nums}.card span{color:var(--mute);font-size:12px}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:7px 10px;border-bottom:1px solid var(--line);
text-align:left;vertical-align:top;white-space:nowrap}tr:last-child td{border-bottom:0}
th{color:var(--mute);font-weight:600;font-size:11px;letter-spacing:.04em;text-transform:uppercase;background:var(--card)}
td.num{text-align:right;font:13px var(--f-mono);font-variant-numeric:tabular-nums}
td.wrapc{white-space:normal;min-width:220px}.ok{color:var(--ok)}.bad{color:var(--bad)}.mute{color:var(--mute)}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600}
.p-ok{background:var(--okbg);color:var(--ok)}.p-bad{background:var(--badbg);color:var(--bad)}
.lv{font-weight:600}.lv-Өндөр{color:var(--hi)}.lv-Дунд{color:var(--mid)}.lv-Бага{color:var(--lo)}
.scale{position:relative;width:120px;height:8px;border-radius:4px;background:var(--track);margin-top:6px}
.scale .t{position:absolute;top:-3px;width:1px;height:14px;background:var(--mute);opacity:.55}
.scale .dot{position:absolute;top:-2px;width:12px;height:12px;border-radius:50%;margin-left:-6px;
border:2px solid var(--card)}.dot.lv-Өндөр{background:var(--hi)}.dot.lv-Дунд{background:var(--mid)}
.dot.lv-Бага{background:var(--lo)}
.bar{height:6px;background:var(--track);border-radius:3px;min-width:60px;margin-top:7px}.bar i{display:block;height:6px;
border-radius:3px;background:var(--acc)}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px}
details+details{margin-top:6px}summary{cursor:pointer;font-weight:600}summary:focus-visible{outline:2px solid var(--acc)}
code{font:12px var(--f-mono)}
"""


OK_PILL, BAD_PILL = "<span class='pill p-ok'>✔</span>", "<span class='pill p-bad'>✘</span>"


def render(rep: dict) -> str:
    s = rep["summary"]
    acts = rep["activities"]
    dates = sorted({a["date"] for a in acts})
    by = {(a["activity"], a["date"]): a for a in acts}
    rows = []
    for aid in sorted({a["activity"] for a in acts}):
        a0 = by[(aid, dates[0])]
        cells = []
        for d in dates:
            a = by[(aid, d)]
            t = "—" if a["total"] is None else f"{a['total']:.2f}"
            cov = 0 if a["coverage"] is None else a["coverage"]
            pos = 0 if a["total"] is None else (a["total"] - 1) / 4 * 100
            meter = ("" if a["total"] is None else
                     f"<div class='scale' title='1 … 5, босго 2.5 / 3.5'><span class='t' style='left:37.5%'></span>"
                     f"<span class='t' style='left:62.5%'></span><span class='dot lv-{_e(a['level'])}' "
                     f"style='left:{pos:.1f}%'></span></div>")
            cells.append(f"<td class='num'>{t}</td><td><span class='lv lv-{_e(a['level'])}'>{_e(a['level']) or '—'}</span>"
                         f"{meter}</td>"
                         f"<td class='num'>{a['n_scored']}/{a['n']}</td>"
                         f"<td><div class='bar'><i style='width:{cov * 100:.0f}%'></i></div></td>"
                         f"<td>{OK_PILL if a['ok'] else BAD_PILL}</td>")
        rows.append(f"<tr><td class='num'>{a0['group']}</td><td>{_e(a0['branch'])}</td><td class='wrapc'>{_e(a0['name'])}</td>"
                    + "".join(cells) + f"<td class='mute'>{_e(by[(aid, dates[-1])]['sols'])}</td></tr>")
    head = "".join(f"<th>{d}</th><th>түвшин</th><th>оноотой</th><th>жингийн хамралт</th><th>тулгалт</th>" for d in dates)
    kinds = {"shared": "Нийтлэг тооцоолол (calc)", "sql": "Өөрийн SQL", "manual": "Гарын үнэлгээ", "empty": "Source 0 мөр"}
    kind_rows = "".join(
        f"<tr><td>{_e(kinds.get(k, k))}</td><td class='num ok'>{s['by_kind'].get(k + '|True', 0)}</td>"
        f"<td class='num {'bad' if s['by_kind'].get(k + '|False', 0) else ''}'>{s['by_kind'].get(k + '|False', 0)}</td></tr>"
        for k in kinds)
    bad = [c for c in rep["checks"] if not c["ok"]]
    bad_html = "".join(f"<tr><td>{_e(c['indicator'])}</td><td>{_e(c['date'])}</td><td class='wrapc'>{_e(c['detail'])}</td></tr>"
                       for c in bad[:200]) or "<tr><td colspan=3 class='ok'>Зөрүү алга — бүгд эталонтой таарсан</td></tr>"
    cases = "".join(f"<tr><td>{OK_PILL if c['ok'] else BAD_PILL}</td>"
                    f"<td>{_e(c['case'])}</td><td class='wrapc mute'>{_e(c['detail'])}</td></tr>" for c in rep["cases"])
    steps = "".join(f"<tr><td>{'✔' if x['rc'] == 0 else '✘'}</td><td>{_e(x['step'])}</td><td class='num'>{x['seconds']}s</td>"
                    f"<td class='wrapc mute'>{_e(x['note'])}</td></tr>" for x in rep["steps"])
    ex = []
    for e in rep["examples"]:
        sols = "".join(f"<tr><td>{_e(r['sol'])}</td><td class='num'>{_n(r['num'])}</td><td class='num'>{_n(r['den'])}</td>"
                       f"<td class='num'>{_n(r['value'], e['unit'])}</td><td>{_e(r['text'])}</td></tr>" for r in e["sols"])
        src = f"calc {e['calc']}" if e["calc"] else "өөрийн SQL"
        ex.append(f"<details><summary>{_e(e['indicator'])} — {_e(e['name'])} <span class='mute'>· {src} · "
                  f"{_e(e['period'])} {e['start']}… · утга {_n(e['value'], e['unit'])} {'; '.join(e['texts'])} · оноо "
                  f"{_n(e['score'])} · жин {_n(e['weight'])}%</span></summary>"
                  f"<p class='mute'>{_e(e['level'])} түвшин: Σ тоологч {_n(e['num'])} / Σ хуваарь {_n(e['den'])}</p>"
                  + (f"<div class='wrap'><table><tr><th>{'SOL' if e['level'] == 'SOL' else 'нэгж'}</th><th>тоологч</th>"
                     f"<th>хуваарь</th><th>утга</th><th>текст</th></tr>{sols}</table></div>" if sols else "")
                  + "</details>")
    master = defaultdict(list)
    for m in rep["master"]:
        master[m["scale"]].append(m["indicator"])
    master_html = "".join(f"<tr><td class='wrapc'><code>{_e(k)}</code></td><td class='wrapc'>{_e(', '.join(sorted(set(v))))}</td></tr>"
                          for k, v in master.items())
    db = "".join(f"<tr><td>{_e(k)}</td><td class='num'>{v:,}</td></tr>" for k, v in sorted(rep["db"].items()))
    kinds_mn = {"shared": "нийтлэг SQL", "sql": "өөрийн SQL", "manual": "гарын"}
    defs_html = "".join(
        f"<tr><td><code>{_e(e['def'])}</code></td><td class='wrapc'>{_e(e['name'])}</td>"
        f"<td>{'нийтлэг · ' if e['common'] else ''}{kinds_mn.get(e['mode'], e['mode'])}</td>"
        f"<td class='num'>{e['acts']}</td><td>{OK_PILL if e['ok'] == e['n'] else BAD_PILL} {e['ok']}/{e['n']}</td></tr>"
        for e in rep["definitions"] if e["common"] or e["mode"] != "manual")
    defs_html += (f"<tr><td colspan=5 class='mute'>+ ганц үйл ажиллагааны гарын "
                  f"{sum(1 for e in rep['definitions'] if not e['common'] and e['mode'] == 'manual')} тодорхойлолт — "
                  f"бүгд {'таарсан' if all(e['ok'] == e['n'] for e in rep['definitions']) else 'зөрүүтэй байна'}"
                  f"</td></tr>")
    return f"""<!doctype html><html lang="mn"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Эрсдэлийн үнэлгээний DEMO</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=Onest:wght@600&display=swap">
<style>{CSS}</style></head><body><main>
<div class="eyebrow">Тулгалтын тайлан · tests/local/demo_check.py</div>
<h1>Эрсдэлийн үнэлгээ — стандарт банкны DEMO</h1>
<p class="lead">master.xlsx-ийн 35 үйл ажиллагаа, 1,382 үзүүлэлт · Oracle (COREMIS, FINACLE, ERP, CARDZONE, JIRA) +
ClickHouse source → <code>risk_assessment_local.ri_result</code> · эталон нь SQL-ээс үл хамааран Python-оор тооцсон ·
{_e(rep['finished'])} · {rep['seconds']}s</p>
<div class="cards">
<div class="card"><b class="{'ok' if s['ok'] == s['checks'] else 'bad'}">{s['ok']}/{s['checks']}</b><span>үзүүлэлт × улирал эталонтой таарсан</span></div>
<div class="card"><b class="{'ok' if s['acts_ok'] == s['acts'] else 'bad'}">{s['acts_ok']}/{s['acts']}</b><span>үйл ажиллагааны нийт оноо, түвшин</span></div>
<div class="card"><b class="{'ok' if s['cases_ok'] == s['cases'] else 'bad'}">{s['cases_ok']}/{s['cases']}</b><span>хамгаалалт, давтан ажиллуулалт, бүтэц, auto</span></div>
<div class="card"><b class="{'ok' if rep['verify_rc'] == 0 else 'bad'}">{'0 зөрүү' if rep['verify_rc'] == 0 else 'зөрүүтэй'}</b><span>ri.py verify (source ↔ ClickHouse)</span></div>
</div>
<h2>Үйл ажиллагааны нийт оноо (Σ жин × оноо / Σ оноотой жин)</h2>
<div class="wrap"><table><tr><th>бүлэг</th><th>BRANCHID</th><th>үйл ажиллагаа</th>{head}<th>SOLID (Q3)</th></tr>{''.join(rows)}</table></div>
<p class="mute">Жингийн хамралт = оноо авсан үзүүлэлтийн жин / нийт жин. Гарын үнэлгээний ~8% нь бөглөгдөөгүй, ~4% нь
«Үнэлэхгүй» (DEMO). BRANCHID 9002, 9010, 9011, 9020, 9021 нь ТОДРУУЛАХ 5 бүлэгт зөвхөн local demo-д өгсөн түр дугаар.</p>
<h2>Тодорхойлолт бүрээр ({len(rep['definitions'])}: давхардалгүй, хуулбар бүр × улирал)</h2>
<div class="wrap"><table><tr><th>тодорхойлолт</th><th>нэр</th><th>төрөл</th><th>үйл ажиллагаа</th><th>тулгалт</th></tr>
{defs_html}</table></div>
<h2>Эталонтой тулгалт</h2>
<div class="wrap"><table><tr><th>төрөл</th><th>таарсан</th><th>зөрүүтэй</th></tr>{kind_rows}</table></div>
<h2>Зөрүү</h2><div class="wrap"><table><tr><th>үзүүлэлт</th><th>өдөр</th><th>тайлбар</th></tr>{bad_html}</table></div>
<h2>Тохиолдлууд</h2><div class="wrap"><table>{cases}</table></div>
<h2>act_01 ба act_40 — үзүүлэлт бүр (2026-Q3, эталон)</h2>{''.join(ex)}
<h2>Мастерийн шатлал стандарт бус (автомат үзүүлэлт — оноо нь мастерийн бичиглэлээр)</h2>
<div class="wrap"><table><tr><th>шатлал (master.xlsx)</th><th>үзүүлэлт</th></tr>{master_html or "<tr><td colspan=2>алга</td></tr>"}</table></div>
<h2>Алхмууд</h2><div class="wrap"><table>{steps}</table></div>
<h2>Demo DB (мөрийн тоо)</h2><div class="wrap"><table>{db}</table></div>
</main></body></html>"""


if __name__ == "__main__":
    sys.exit(main())
