"""Үзүүлэлт БҮРИЙН тест (DB-гүй): activities/-ийн 1,388 үзүүлэлт, нийтлэг тодорхойлолт бүр тусдаа тест.

    pytest tests/unit/test_catalog.py -q                 # бүгд
    pytest tests/unit/test_catalog.py -k RI_40_1545      # нэг үзүүлэлт
    pytest tests/unit/test_catalog.py -rx                # master-ийн эвдэрсэн шатлал (xfail) — гараар засна

Шалгах: тохиргоо алдаагүй, жин > 0, шатлал задардаг (автомат үзүүлэлтэд заавал; гарынх эвдэрсэн бол xfail),
хамрах хугацаа, нийтлэг тодорхойлолт / SQL файл байгаа, SQL-ийн static дүрэм (DML, dialect, стандарт багана).
Утга зөв эсэхийг demo DB дээр tests/local/demo_check.py (эталон) шалгана.
"""
import pytest

from ri_runner.checks import check_sql
from ri_runner.config import known_connections
from ri_runner.metadata import PERIODS, load_catalog

CAT = load_catalog()
CONNS = known_connections()
INDICATORS = sorted(CAT.indicators)
DEFINITIONS = sorted(CAT.calcs)


def test_catalog_loads():
    assert not CAT.errors, CAT.errors[:5]
    assert len(CAT.activities) >= 35 and len(INDICATORS) >= 1380
    assert len({i.indicator_id for i in CAT.indicators.values()}) == len(INDICATORS)


@pytest.mark.parametrize("iid", INDICATORS)
def test_indicator(iid):
    ind = CAT.indicators[iid]
    assert not ind.errors, ind.errors
    assert ind.period in PERIODS
    act = CAT.activities[ind.activity_id]
    assert ind.indicator_id.startswith(f"RI_{act.group_no:02d}_")
    extra = int(iid[-4:]) >= 9000
    if not ind.example and not extra:
        assert ind.weight and ind.weight > 0, "жин алга"
    if ind.mode in ("shared", "sql"):
        calc = CAT.calcs.get(ind.calc) if ind.mode == "shared" else ind
        assert calc is not None and calc.sql_path.exists(), "SQL / тодорхойлолтын файл алга"
        assert not CONNS or calc.connection in CONNS
        if not extra and not ind.example:
            assert ind.scale and not ind.scale_error, f"автомат үзүүлэлтийн шатлал задарсангүй: {ind.scale_error}"
    elif ind.scale_error or not ind.scale:
        pytest.xfail(f"master-ийн шатлал задарсангүй ({ind.scale_error}) — master.xlsx-ийг гараар засна")


@pytest.mark.parametrize("cid", DEFINITIONS)
def test_definition(cid):
    calc = CAT.calcs[cid]
    assert not calc.errors, calc.errors
    users = [i for i in CAT.indicators.values() if (i.calc or i.def_id) == cid]
    assert users, "ямар ч үзүүлэлт ашиглаагүй"
    if calc.mode == "sql" and not calc.sql_from:
        errors, _ = check_sql(calc, CONNS.get(calc.connection))
        assert not errors, errors
    if calc.sql_from:
        assert CAT.get(calc.sql_from) is not None
