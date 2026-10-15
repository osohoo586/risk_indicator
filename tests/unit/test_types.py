import datetime as dt
import decimal

import pytest

from ri_runner.db import classify_error, convert_value, nullable, oracle_to_ch_type, type_family, RunnerError


class T:
    def __init__(self, name):
        self.name = name


@pytest.mark.parametrize("name,p,s,expected", [
    ("DB_TYPE_NUMBER", 10, 0, "Nullable(Int64)"),
    ("DB_TYPE_NUMBER", 20, 0, "Nullable(Decimal(20, 0))"),     # урт ID — Float болох ёсгүй
    ("DB_TYPE_NUMBER", 18, 2, "Nullable(Decimal(18, 2))"),
    ("DB_TYPE_NUMBER", 0, -127, "Nullable(Float64)"),          # SUM(), COUNT() гэх мэт
    ("DB_TYPE_DATE", None, None, "Nullable(DateTime64(0))"),   # 1900 оны огноо багтана
    ("DB_TYPE_TIMESTAMP", None, None, "Nullable(DateTime64(6))"),
    ("DB_TYPE_VARCHAR", None, None, "Nullable(String)"),
])
def test_oracle_to_ch_type(name, p, s, expected):
    assert oracle_to_ch_type(T(name), p, s) == expected


def test_nullable():
    assert nullable("Int64") == "Nullable(Int64)"
    assert nullable("Nullable(Nothing)") == "Nullable(String)"     # бүх утга NULL
    assert nullable("LowCardinality(String)") == "LowCardinality(String)"


def test_convert_value():
    assert convert_value(12345678901234567890, "Nullable(Decimal(20, 0))") == decimal.Decimal("12345678901234567890")
    assert convert_value(dt.date(1900, 1, 1), "Nullable(DateTime64(0))") == dt.datetime(1900, 1, 1)
    assert convert_value(float("nan"), "Nullable(Float64)") is None
    assert convert_value(101, "Nullable(String)") == "101"
    assert convert_value(None, "Nullable(Int64)") is None
    assert convert_value(dt.datetime(2026, 9, 30, 10, 0), "Nullable(Date)") == dt.date(2026, 9, 30)


@pytest.mark.parametrize("a,b,same", [
    ("Nullable(Int64)", "Nullable(Float64)", True),     # тоо ↔ тоо: зөвшөөрнө
    ("Nullable(String)", "Nullable(Int64)", False),     # текст ↔ тоо: түгжинэ
    ("Nullable(DateTime64(0))", "Date", True),
    ("LowCardinality(String)", "Nullable(String)", True),
])
def test_type_family(a, b, same):
    assert (type_family(a) == type_family(b)) is same


def test_classify_error():
    assert classify_error(RunnerError("COLUMN_NAME", "x")) == ("COLUMN_NAME", "x")
    assert classify_error(Exception("ORA-00942: table or view does not exist"))[0] == "ORA-00942"
    assert classify_error(Exception("DPY-4024: call timeout"))[0] == "TIMEOUT"
    assert classify_error(Exception("Code: 47. DB::Exception"))[0] == "CH-47"
