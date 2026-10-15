"""Дутуу / хуучирсан үр дүнг олж ЗӨВХӨН тэдгээрийг ажиллуулна (давтан ажиллуулахад аюулгүй) — prod DAG.

    python ri.py auto --env prod --all --plan                 # юу, яагаад ажиллахыг харуулна
    python ri.py auto --env prod --all [--as-of 2026-10-14] [--since 2025-10-01]

Тайлант өдрүүд: [since, as_of] доторх үзүүлэлт бүрийн frequency-ийн огноо (quarterly → улирлын сүүл).
Хугацааны эхлэл нь үзүүлэлтийн period-оос (report / last_year / since_audit / latest) — run-тай ижил.
Шалтгаан (audit + ri_result-ээс):
  ШИНЭ          үр дүн, бодит оролдлого аль аль нь алга (SOURCE_NOT_READY г.м. SKIPPED-ийг тооцохгүй)
  АЛДАА         сүүлийн оролдлого FAILED / TIMEOUT / VALIDATION_FAILED
  ӨӨРЧЛӨГДСӨН   sql_version өөр: үзүүлэлтийн файл, нийтлэг тооцоолол, shared/, config params өөрчлөгдсөн
  ХАМААРАЛ      dependency нь мөн өдөр дахин ажиллана
manual үзүүлэлт орохгүй (ri.py manual). Ажилласны дараа үйл ажиллагааны нийт оноо дахин тооцогдоно.
"""
import datetime as dt

from . import store
from .dates import is_due, to_date
from .db import connect
from .metadata import Indicator
from .runner import PROBLEM_STATUSES, RunContext, version_of

REASONS = ("ШИНЭ", "АЛДАА", "ӨӨРЧЛӨГДСӨН", "ХАМААРАЛ")


def due_dates(ind: Indicator, since: dt.date, as_of: dt.date) -> list[dt.date]:
    out, d = [], since
    while d <= as_of:
        if is_due(ind.frequency, d):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def build_plan(ctx: RunContext, runnable: list[Indicator], since: dt.date, as_of: dt.date):
    """({тайлант өдөр: [үзүүлэлт]}, [(үзүүлэлт, өдөр, шалтгаан, тайлбар)])."""
    cfg, cat = ctx.cfg, ctx.cat
    with connect(cfg, cfg.result_connection) as conn:
        store.ensure_base(cfg, conn, log=lambda *_: None)
        written = {(i, to_date(d)): v for (i, d), v in store.written_versions(cfg, conn, since, as_of).items()}
        attempts = {(i, to_date(d)): sv for (i, d), sv in store.last_attempts(cfg, conn, since, as_of).items()}
    reasons: dict[tuple, tuple] = {}
    for ind in runnable:
        cur = version_of(cat, ind)
        for d in due_dates(ind, since, as_of):
            key = (ind.indicator_id, d)
            last = attempts.get(key)
            have = written.get(key)
            if last is None and have is None:
                reasons[key] = ("ШИНЭ", "үр дүн алга")
            elif last is not None and last[0] in PROBLEM_STATUSES:
                reasons[key] = ("АЛДАА", f"сүүлийн оролдлого {last[0]}")
            elif (have or (last[1] if last else None)) != cur:
                reasons[key] = ("ӨӨРЧЛӨГДСӨН", f"{have or last[1]} → {cur}")
    # Хамаарал: dependency нь ажиллах бол түүнийг ашигладаг үзүүлэлт ч мөн өдөр
    by_id = {i.indicator_id: i for i in runnable}
    changed = True
    while changed:
        changed = False
        for ind in runnable:
            for dep in ind.dependencies:          # нийтлэг тооцоолол нь version_of-д орсон (ӨӨРЧЛӨГДСӨН)
                for (iid, d), _ in list(reasons.items()):
                    if iid == dep and (ind.indicator_id, d) not in reasons and d in due_dates(ind, d, d):
                        reasons[(ind.indicator_id, d)] = ("ХАМААРАЛ", f"{dep} дахин ажиллана")
                        changed = True
    plan: dict[dt.date, list] = {}
    for (iid, d) in sorted(reasons, key=lambda k: (k[1], k[0])):
        plan.setdefault(d, []).append(by_id[iid])
    return plan, [(by_id[i], d, *reasons[(i, d)]) for i, d in sorted(reasons, key=lambda k: (k[1], k[0]))]


def print_plan(items: list, since: dt.date, as_of: dt.date) -> None:
    if not items:
        print(f"AUTO {since} … {as_of}: бүх үр дүн шинэчлэгдсэн, ажиллуулах зүйл алга.")
        return
    counts = {r: sum(1 for x in items if x[2] == r) for r in REASONS}
    print(f"AUTO {since} … {as_of}: {len(items)} (үзүүлэлт × өдөр) — "
          + ", ".join(f"{r} {n}" for r, n in counts.items() if n))
    for ind, d, reason, why in items[:200]:
        print(f"  {d}  {ind.indicator_id:<11} {reason:<12} {why}")
    if len(items) > 200:
        print(f"  … +{len(items) - 200}")
