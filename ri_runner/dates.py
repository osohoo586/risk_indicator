"""Тайлант огноо, frequency, period параметрүүд."""
import calendar
import datetime as dt


def month_end(d: dt.date) -> dt.date:
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def is_month_end(d: dt.date) -> bool:
    return d == month_end(d)


def quarter_start(d: dt.date) -> dt.date:
    return dt.date(d.year, 3 * ((d.month - 1) // 3) + 1, 1)


def is_due(frequency: str, d: dt.date) -> bool:
    if frequency == "daily":
        return True
    if frequency == "semimonthly":
        return d.day == 15 or is_month_end(d)
    if frequency == "monthly":
        return is_month_end(d)
    if frequency == "quarterly":
        return is_month_end(d) and d.month in (3, 6, 9, 12)
    if frequency == "yearly":
        return d.month == 12 and d.day == 31
    return False


def period_params(frequency: str, d: dt.date) -> dict:
    """SQL-д өгөх огнооны параметрүүд.

    p_report_date      тайлант өдөр
    p_period_start     тухайн үеийн эхний өдөр (daily: тэр өдөр, monthly: сарын 1, ...)
    p_period_end       = p_report_date
    p_prev_period_end  өмнөх үеийн сүүлийн өдөр (monthly: өмнөх сарын сүүл, ...)
    p_report_date_next тайлант өдөр + 1 (цагтай баганад: col < :p_report_date_next)
    Ижил утгатай нэрс: p_date_from (= p_period_start), p_date_to (= p_report_date), p_date_to_next.
    """
    if frequency == "daily":
        start, prev_end = d, d - dt.timedelta(days=1)
    elif frequency in ("monthly", "semimonthly"):
        start = d.replace(day=1)
        prev_end = start - dt.timedelta(days=1)
    elif frequency == "quarterly":
        start = quarter_start(d)
        prev_end = start - dt.timedelta(days=1)
    elif frequency == "yearly":
        start = dt.date(d.year, 1, 1)
        prev_end = start - dt.timedelta(days=1)
    else:
        start, prev_end = d, d - dt.timedelta(days=1)
    return with_aliases({
        "p_report_date": d,
        "p_report_date_next": d + dt.timedelta(days=1),   # "< :p_report_date_next" → тайлант өдрийг бүтэн оруулна
        "p_period_start": start,
        "p_period_end": d,
        "p_prev_period_end": prev_end,
    })


def with_aliases(params: dict) -> dict:
    """Procedure-уудын нэршлээр: :p_date_from = :p_period_start, :p_date_to = :p_report_date."""
    return {**params, "p_date_from": params["p_period_start"], "p_date_to": params["p_report_date"],
            "p_date_to_next": params["p_report_date_next"]}


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Огноо YYYY-MM-DD хэлбэртэй байх ёстой: {value}") from exc


def parse_period(value) -> tuple[dt.date, dt.date]:
    """Тайлангийн хугацаа → (эхлэх, дуусах) огноо.

    2026-Q3     → 2026-07-01 … 2026-09-30   (улирал)
    2026-09     → 2026-09-01 … 2026-09-30   (сар)
    2026-H2     → 2026-07-01 … 2026-12-31   (хагас жил)
    2026        → 2026-01-01 … 2026-12-31   (жил)
    2026-09-30  → 2026-09-30 … 2026-09-30   (нэг өдөр)
    """
    import re
    v = str(value).strip().upper()
    if m := re.fullmatch(r"(\d{4})-Q([1-4])", v):
        y, q = int(m.group(1)), int(m.group(2))
        start = dt.date(y, 3 * q - 2, 1)
        return start, month_end(dt.date(y, 3 * q, 1))
    if m := re.fullmatch(r"(\d{4})-H([12])", v):
        y, h = int(m.group(1)), int(m.group(2))
        return dt.date(y, 6 * h - 5, 1), month_end(dt.date(y, 6 * h, 1))
    if m := re.fullmatch(r"(\d{4})-(\d{2})", v):
        start = dt.date(int(m.group(1)), int(m.group(2)), 1)
        return start, month_end(start)
    if m := re.fullmatch(r"(\d{4})", v):
        y = int(m.group(1))
        return dt.date(y, 1, 1), dt.date(y, 12, 31)
    try:
        d = dt.date.fromisoformat(v)
        return d, d
    except ValueError:
        raise ValueError(f"Хугацаа буруу: {value}. Жишээ: 2026-Q3, 2026-09, 2026-H2, 2026, 2026-09-30") from None


def to_date(value) -> dt.date:
    """DB-ээс ирсэн утгыг (datetime / date / 'YYYY-MM-DD') date болгоно."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value)[:10])


def date_range(start: dt.date, end: dt.date) -> list[dt.date]:
    return [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
