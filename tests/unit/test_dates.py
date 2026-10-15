import datetime as dt

import pytest

from ri_runner.dates import is_due, parse_period, period_params

D = dt.date


@pytest.mark.parametrize("freq,day,due", [
    ("daily", D(2026, 9, 17), True),
    ("monthly", D(2026, 9, 30), True),
    ("monthly", D(2026, 9, 29), False),
    ("monthly", D(2024, 2, 29), True),           # өндөр жил
    ("semimonthly", D(2026, 9, 15), True),
    ("semimonthly", D(2026, 9, 16), False),
    ("quarterly", D(2026, 9, 30), True),
    ("quarterly", D(2026, 8, 31), False),
    ("quarterly", D(2026, 12, 31), True),
    ("yearly", D(2026, 12, 31), True),
    ("yearly", D(2026, 9, 30), False),
])
def test_is_due(freq, day, due):
    assert is_due(freq, day) is due


def test_period_params_quarterly():
    p = period_params("quarterly", D(2026, 9, 30))
    assert p["p_period_start"] == D(2026, 7, 1)
    assert p["p_period_end"] == p["p_report_date"] == D(2026, 9, 30)
    assert p["p_prev_period_end"] == D(2026, 6, 30)
    assert p["p_report_date_next"] == D(2026, 10, 1)


def test_period_params_monthly_and_daily():
    assert period_params("monthly", D(2026, 3, 31))["p_period_start"] == D(2026, 3, 1)
    assert period_params("monthly", D(2026, 3, 31))["p_prev_period_end"] == D(2026, 2, 28)
    assert period_params("daily", D(2026, 1, 1))["p_prev_period_end"] == D(2025, 12, 31)


@pytest.mark.parametrize("text,start,end", [
    ("2026-Q3", D(2026, 7, 1), D(2026, 9, 30)),
    ("2026-q1", D(2026, 1, 1), D(2026, 3, 31)),
    ("2026-09", D(2026, 9, 1), D(2026, 9, 30)),
    ("2026-H2", D(2026, 7, 1), D(2026, 12, 31)),
    ("2026", D(2026, 1, 1), D(2026, 12, 31)),
    ("2026-09-30", D(2026, 9, 30), D(2026, 9, 30)),
])
def test_parse_period(text, start, end):
    assert parse_period(text) == (start, end)


def test_parse_period_invalid():
    with pytest.raises(ValueError):
        parse_period("2026-Q5")
