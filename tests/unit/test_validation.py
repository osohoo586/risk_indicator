import datetime as dt
from types import SimpleNamespace

import pytest

from ri_runner.db import RunnerError
from ri_runner.runner import _id, _to_rows, aggregate, change_check, validate_calc
from ri_runner.store import check_standard_columns


def calc(**kw):
    base = dict(value_range=None, empty_source="warn", min_rows=None)
    base.update(kw)
    return SimpleNamespace(**base)


def row(eid, value=None, num=None, den=None, level="SOL", metric="value"):
    return {"entity_level": level, "entity_id": eid, "entity_name": None, "metric": metric,
            "numerator": num, "denominator": den, "value": value, "source_row_count": 1, "data_status": "OK"}


def statuses(checks):
    return {name: st for name, st, _ in checks}


def test_duplicate_entity_fails():
    rows = [row("101", 1), row("101", 2), row("102", 3)]
    assert statuses(validate_calc(calc(), rows))["duplicate"] == "FAIL"
    assert statuses(validate_calc(calc(), rows[1:]))["duplicate"] == "PASS"
    # өөр METRIC бол давхардал биш
    assert statuses(validate_calc(calc(), [row("101", 1), row("101", 2, metric="cnt")]))["duplicate"] == "PASS"


def test_min_rows_empty_id_and_range():
    rows = [row("101", 0.5), row("", 2.0)]
    st = statuses(validate_calc(calc(min_rows=3, value_range={"min": 0, "max": 1}), rows))
    assert st["min_rows"] == "FAIL" and st["entity"] == "FAIL" and st["value_range"] == "FAIL"


def test_empty_rows():
    assert statuses(validate_calc(calc(), []))["no_source_data"] == "WARN"
    assert statuses(validate_calc(calc(empty_source="fail"), []))["no_source_data"] == "FAIL"
    assert statuses(validate_calc(calc(min_rows=1), []))["no_source_data"] == "FAIL"


@pytest.mark.parametrize("new,prev,pct,expected", [
    (130, 100, 30, "PASS"),
    (131, 100, 30, "WARN"),
    (69, 100, 30, "WARN"),
    (0, 0, 30, "PASS"),
    (5, 0, 30, "WARN"),
])
def test_change_check(new, prev, pct, expected):
    assert change_check(new, "2026-06-30", prev, pct)[0] == expected


def test_change_check_first_period():
    assert change_check(100, None, None, 30)[0] == "PASS"


def test_standard_columns():
    check_standard_columns(["ENTITY_LEVEL", "ENTITY_ID", "VALUE", "NUMERATOR", "DENOMINATOR"])
    for bad in (["ENTITY_ID", "VALUE"], ["ENTITY_LEVEL", "ENTITY_ID", "VALUE", "SOL_ID"],
                ["ENTITY_LEVEL", "ENTITY_ID", "VALUE", "VALUE"]):
        with pytest.raises(RunnerError):
            check_standard_columns(bad)


def test_ratio_rollup_is_sum_over_sum_not_average():
    # 1/2 = 0.5 ба 90/100 = 0.9 → дундаж 0.7 биш, 91/102
    agg = aggregate([row("1", 0.5, 1, 2), row("2", 0.9, 90, 100)])["value"]
    assert agg["value"] == pytest.approx(91 / 102)
    assert agg["numerator"] == 91 and agg["denominator"] == 102


def test_sum_rollup_and_zero_denominator():
    assert aggregate([row("1", 3), row("2", 4)])["value"]["value"] == 7
    assert aggregate([row("1", 3, 3, 1), row("2", 4, 4, 2)], {"value": "sum"})["value"]["value"] == 7
    z = aggregate([row("1", None, 5, 0)])["value"]
    assert z["value"] is None and z["data_status"] == "ZERO_DENOMINATOR"


def test_entity_id_normalized():
    assert [_id(x) for x in (101, 101.0, " 101 ", "101.0", None, "A1")] == ["101", "101", "101", "101", "", "A1"]


def test_to_rows_defaults():
    rows = _to_rows(["ENTITY_LEVEL", "ENTITY_ID", "VALUE"], [("sol", 101.0, 2)])
    assert rows[0]["entity_level"] == "SOL" and rows[0]["entity_id"] == "101"
    assert rows[0]["metric"] == "value" and rows[0]["value"] == 2.0


def test_activity_rows_filters_by_branch_sols(tmp_path, monkeypatch):
    from ri_runner import orgmap
    from ri_runner.runner import activity_rows
    units = tmp_path / "u.csv"
    units.write_text("BRANCHNAME,SOLID,BRANCHID,SUBBRANCHID,TDATE\n"
                     "a,101,998,998,2026-06-01\nb,102,998,998,2026-06-01\nc,102,1162,1162,2026-06-01\n"
                     "a,101,998,998,2026-09-15\n", encoding="utf-8")
    monkeypatch.setitem(orgmap._PATHS, "activity_units", units)
    orgmap.clear_cache()
    try:
        ind = SimpleNamespace(rollup_metrics={})
        act = SimpleNamespace(branch_id="998", activity_id="ACT_01")
        rows = [row("101", None, 10, 20), row("102", None, 30, 40), row("103", None, 1, 1)]
        agg, drill, _ = activity_rows(ind, act, rows, dt.date(2026, 6, 30))
        assert agg["value"]["value"] == pytest.approx(40 / 60) and len(drill) == 2
        # 2026-09-15 snapshot: 998 = зөвхөн 101
        agg, drill, _ = activity_rows(ind, act, rows, dt.date(2026, 9, 30))
        assert agg["value"]["value"] == pytest.approx(0.5) and [d["entity_id"] for d in drill] == ["101"]
        # 102 нь 1162-д ч бас (олон үйл ажиллагаанд)
        act2 = SimpleNamespace(branch_id="1162", activity_id="ACT_03")
        agg, _, _ = activity_rows(ind, act2, rows, dt.date(2026, 6, 30))
        assert agg["value"]["value"] == pytest.approx(0.75)
        # тэгээр эхэлсэн SOL ("0101") таарна
        agg, drill, _ = activity_rows(ind, act, [row("0101", None, 10, 20)], dt.date(2026, 9, 30))
        assert agg["value"]["value"] == 0.5 and drill[0]["entity_name"] == "a"
        # нэг ч SOL таараагүй бол WARN
        _, _, checks = activity_rows(ind, act, [row("555", None, 1, 1)], dt.date(2026, 9, 30))
        assert any(n == "units_match" and st == "WARN" for n, st, _ in checks)
        # BRANCHID-гүй үйл ажиллагаа SOL мөрийг нэгтгэж чадахгүй
        with pytest.raises(RunnerError):
            activity_rows(ind, SimpleNamespace(branch_id="", activity_id="ACT_02"), rows, dt.date(2026, 6, 30))
    finally:
        orgmap.clear_cache()


def test_count_without_denominator_is_summed_and_text_only_is_data():
    """Гомдлын тоо (NUMERATOR, VALUE, хуваарьгүй) → Σ VALUE; зөвхөн VALUE_TEXT (ангилал) → NO_DATA биш."""
    rows = [{"metric": "value", "numerator": 3.0, "denominator": None, "value": 0.5, "value_text": None},
            {"metric": "value", "numerator": 6.0, "denominator": None, "value": 1.0,
             "value_text": "ДАГ-т гомдол ирж, шалгагдсан."}]
    a = aggregate(rows)["value"]
    assert a["value"] == 1.5 and a["numerator"] == 9.0 and a["data_status"] == "OK"
    assert a["value_texts"] == ["ДАГ-т гомдол ирж, шалгагдсан."]
    only_text = aggregate([{"metric": "value", "numerator": None, "denominator": None, "value": None,
                            "value_text": "Зөрчилгүй"}])["value"]
    assert only_text["value"] is None and only_text["data_status"] == "OK"
