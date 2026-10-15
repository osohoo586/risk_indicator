"""Ахицын тайлан: metadata (+ хүсвэл audit-ийн сүүлийн төлөв)."""
import csv
import datetime as dt

from .config import OUTPUT_DIR
from .metadata import STATUSES, Catalog

POINTS = {"simple": 1, "medium": 3, "complex": 8}
DONE_STATUSES = ("TESTED", "DONE")


def build_rows(cat: Catalog, last_runs: dict | None = None) -> list[dict]:
    rows = []
    for ind in sorted(cat.indicators.values(), key=lambda i: i.indicator_id):
        if ind.example:
            continue
        last = (last_runs or {}).get(ind.indicator_id, {})
        rows.append({
            "indicator_id": ind.indicator_id,
            "activity_id": ind.activity_id,
            "mode": ind.mode,
            "calc": ind.calc or "",
            "weight": ind.weight,
            "indicator_name_mn": ind.name_mn,
            "indicator_name_en": ind.name_en,
            "owner": ind.owner,
            "reviewer": ind.reviewer,
            "connection": ind.connection,
            "frequency": ind.frequency,
            "complexity": ind.complexity,
            "points": POINTS.get(ind.complexity, 1),
            "status": ind.status,
            "version": ind.version,
            "enabled": ind.enabled,
            "metadata_errors": len(ind.errors),
            "last_run_status": last.get("status", ""),
            "last_run_report_date": last.get("report_date", ""),
            "last_run_at": last.get("at", ""),
            "last_error_code": last.get("error_code", "") or "",
            "has_error": "Y" if (ind.errors or last.get("status") in ("FAILED", "TIMEOUT", "VALIDATION_FAILED")) else "N",
        })
    return rows


def _table(title: str, key: str, rows: list[dict]) -> None:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r[key], []).append(r)
    cols = list(STATUSES) + ["ERROR"]
    print(f"\n{title}")
    header = f"{key:<14}{'total':>7}" + "".join(f"{c:>13}" for c in cols) + f"{'done%':>8}{'done%pts':>10}"
    print(header)
    print("-" * len(header))
    for g in sorted(groups):
        items = groups[g]
        cnt = {s: sum(1 for r in items if r["status"] == s) for s in STATUSES}
        err = sum(1 for r in items if r["has_error"] == "Y")
        done = sum(1 for r in items if r["status"] in DONE_STATUSES)
        pts = sum(r["points"] for r in items)
        done_pts = sum(r["points"] for r in items if r["status"] in DONE_STATUSES)
        print(f"{g:<14}{len(items):>7}" + "".join(f"{cnt[s]:>13}" for s in STATUSES) + f"{err:>13}"
              f"{100 * done / len(items):>7.1f}%{100 * done_pts / pts if pts else 0:>9.1f}%")


def report(cat: Catalog, last_runs: dict | None = None) -> str:
    rows = build_rows(cat, last_runs)
    if not rows:
        print("Үзүүлэлт алга (жишээ activity-г тооцохгүй).")
        return ""
    total = len(rows)
    print(f"Нийт үзүүлэлт: {total}")
    labels = {"TODO": "Хөгжүүлж эхлээгүй", "IN_PROGRESS": "Хөгжүүлж байгаа",
              "REVIEW": "Review хүлээж байгаа", "TESTED": "Test амжилттай", "DONE": "Production-д гарсан"}
    for s in STATUSES:
        print(f"  {labels[s]:<22}{sum(1 for r in rows if r['status'] == s):>6}")
    print(f"  {'Алдаатай':<22}{sum(1 for r in rows if r['has_error'] == 'Y'):>6}")
    modes = {"sql": "Өөрийн SQL", "shared": "Нийтлэг SQL (_shared)", "manual": "Гараар оруулах"}
    print("Горимоор:")
    for m, label in modes.items():
        print(f"  {label:<22}{sum(1 for r in rows if r['mode'] == m):>6}")
    calcs = sorted({r['calc'] for r in rows if r['calc']})
    if calcs:
        print(f"  (нийтлэг тооцоолол {len(calcs)}: нэг SQL → олон үйл ажиллагаа)")
    _table("Хөгжүүлэгч тус бүр", "owner", rows)
    _table("Activity тус бүр", "activity_id", rows)

    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"progress_{dt.date.today():%Y%m%d}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nДэлгэрэнгүй (Excel-ээр нээнэ): {path}")
    return str(path)
