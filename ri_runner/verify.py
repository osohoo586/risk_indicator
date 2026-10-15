"""Дахин тооцоолж ClickHouse-д бичигдсэн үр дүнтэй тулгах (юу ч бичихгүй).

    python ri.py verify --env local activities/act_01_corporate_business/ -p 2026-Q3

Тайлант өдөр бүрт сонгосон үзүүлэлтүүдийн тооцооллыг source дээр ДАХИН (зөвхөн уншиж) ажиллуулж,
ri_result-ийн одоогийн мөртэй тулгана:
  үзүүлэлт   result_number, result (оноо), solid (тайлант өдрийн SOLID-ууд), branch_id, activity_id, нэрс;
             үйл ажиллагаанд яг НЭГ мөр
  audit      үр дүнг бичсэн run-ий audit бүртгэл SUCCESS / WARNING байх
  нийт оноо  TOTAL мөр = ri_result-ийн үзүүлэлтүүдийн оноо × жин (activities/): result_number, result (түвшин)
Нэг ч зөрүү байвал exit 1.
"""
import datetime as dt
import math

from . import store
from .config import load_scoring
from .db import classify_error, connect
from .runner import RunContext, activity_scored, fetch_calc, group_by_calc, target_rows
from .scale import risk_level

_FIELDS = ("result_number", "result", "solid", "branch_id", "activity_id", "activity", "risk_indicator")


def same(a, b) -> bool:
    if a in ("", None) or b in ("", None):
        return a in ("", None) and b in ("", None)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(a, dt.datetime):
        a = a.date()
    if isinstance(b, dt.datetime):
        b = b.date()
    return str(a) == str(b)


def compare(expected: list[dict], got: list[dict]) -> list[str]:
    """Тооцоолсон (runner-ийн дотоод мөрүүд) ↔ ClickHouse-ийн ri_result: зөрүүний жагсаалт (хоосон = яг таарсан)."""
    def key(r):
        return (r["risk_ind_id"], str(r["branch_id"]))
    have = {}
    for r in got:
        if key(r) in have:
            return [f"{key(r)} давхардсан мөр ClickHouse-д"]
        have[key(r)] = r
    out = []
    for e in store.to_result_rows(expected):
        g = have.pop(key(e), None)
        k = f"{e['risk_ind_id']} {e['branch_id']}"
        if g is None:
            out.append(f"{k}: ClickHouse-д алга")
            continue
        diff = [f"{f}: тооцоо={e.get(f)!r} ClickHouse={g.get(f)!r}" for f in _FIELDS if not same(e.get(f), g.get(f))]
        if diff:
            out.append(f"{k}: " + "; ".join(diff[:4]))
    out += [f"{k[0]} {k[1]}: ClickHouse-д илүү мөр" for k in have]
    return out


def recompute(ctx: RunContext, plan: dict) -> dict:
    """{(үзүүлэлт, өдөр): runner-ийн дотоод мөрүүд} — source дээр дахин тооцоолсон, юу ч бичихгүй.
    SOL задаргаа, тоологч / хуваарийг (ri_result-д хадгалахгүй) шалгахад (tests/local/demo_check.py)."""
    from .db import ConnectionPool
    ctx.pool = ctx.pool or ConnectionPool(ctx.cfg)
    out: dict = {}
    try:
        for d in sorted(plan):
            for _, (calc, start, targets) in sorted(group_by_calc(ctx, plan[d], d).items()):
                rows, params = fetch_calc(ctx, calc, d, start, targets[0])
                for t in targets:
                    if rows and ctx.cat.activities[t.activity_id].branch_id:
                        out[(t.indicator_id, d)] = target_rows(ctx, calc, t, rows, params, d)[0]
    finally:
        ctx.pool.close()
        ctx.pool = None
    return out


def verify_plan(ctx: RunContext, plan: dict) -> int:
    """{тайлант өдөр: [үзүүлэлт]} — зөрүүтэй бол 1."""
    from .db import ConnectionPool
    cfg, cat = ctx.cfg, ctx.cat
    ctx.pool = ctx.pool or ConnectionPool(cfg)
    n_ok = n_bad = n_skip = 0
    scoring = load_scoring(cfg)
    with connect(cfg, cfg.result_connection) as res:
        for d in sorted(plan):
            touched = set()
            for _, (calc, start, targets) in sorted(group_by_calc(ctx, plan[d], d).items()):
                try:
                    rows, params = fetch_calc(ctx, calc, d, start, targets[0])
                    err = None
                except Exception as exc:  # noqa: BLE001
                    rows, params, err = [], {}, "%s: %s" % classify_error(exc)
                for t in targets:
                    act = cat.activities[t.activity_id]
                    got = store.read_indicator(cfg, res, t.indicator_id, d)
                    tag = f"{t.indicator_id} {d}"
                    if err:
                        print(f"  ✘ {tag}  source дээр дахин ажиллуулж чадсангүй — {err[:200]}")
                        n_bad += 1
                        continue
                    if not act.branch_id:
                        print(f"  – {tag}  BRANCHID алга — алгасав")
                        n_skip += 1
                        continue
                    if not rows and not got:
                        print(f"  – {tag}  source 0 мөр, ClickHouse-д ч мөр алга (WARNING-аар бичигдээгүй)")
                        n_skip += 1
                        continue
                    expected = target_rows(ctx, calc, t, rows, params, d)[0] if rows else []
                    problems = compare(expected, got)
                    run_ids = {g["run_id"] for g in got}
                    if len(run_ids) > 1:
                        problems.append(f"{len(run_ids)} өөр run_id-ийн мөр холилдсон")
                    for rid in run_ids:
                        status, code = store.audit_of_run(cfg, res, rid, t.indicator_id, d)
                        if status not in ("SUCCESS", "WARNING"):
                            problems.append(f"audit (run {rid[:8]}): {status or 'алга'} {code or ''}".strip())
                    a = next((e for e in expected if e["entity_level"] == "ACTIVITY" and e.get("primary")), None)
                    if problems:
                        n_bad += 1
                        print(f"  ✘ {tag}  " + " | ".join(problems[:5]))
                    else:
                        n_ok += 1
                        v = "—" if not a or a.get("value") is None else f"{a['value']:.6g}"
                        sc = "—" if not a or a.get("score") is None else f"{a['score']:g}"
                        print(f"  ✔ {tag}  value={v} score={sc}  ({act.branch_id})")
                    if not t.example:
                        touched.add(t.activity_id)
            for aid in sorted(touched):
                act = cat.activities[aid]
                row = store.read_activity_row(cfg, res, act.branch_id, d)
                inputs = activity_scored(cat, aid, store.activity_inputs(cfg, res, act.branch_id, d))
                sw = sum(w for _, _, w in inputs)
                value = sum(s * w for _, s, w in inputs) / sw if sw else None
                level = risk_level(value, scoring["high"], scoring["medium"])
                if row is None or "_count" in row:
                    n_bad += 1
                    print(f"  ✘ {act.branch_id} {aid} {d} нийт оноо: TOTAL мөр "
                          f"{'алга' if row is None else str(row['_count']) + ' удаа'} — python ri.py aggregate")
                elif not (same(row["result_number"], value) and (row["result"] or "") == (level or "")):
                    n_bad += 1
                    print(f"  ✘ {act.branch_id} {aid} {d} нийт оноо: ClickHouse {row['result_number']} {row['result']} "
                          f"≠ үзүүлэлтүүдээс {value} {level} ({len(inputs)}) — python ri.py aggregate")
                else:
                    n_ok += 1
                    v = "—" if value is None else f"{value:.3f}"
                    print(f"  ✔ {act.branch_id} {aid} {d} нийт оноо {v} {level or '—'} (оноотой {len(inputs)})")
    ctx.pool.close()
    print(f"\nVERIFY: таарсан {n_ok}, зөрүүтэй {n_bad}, алгассан {n_skip}")
    return 1 if n_bad else 0
