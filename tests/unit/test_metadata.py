from ri_runner.metadata import load_catalog, split_front_matter

ACTIVITY = """activity_id: ACT_05
activity_name_mn: Тест
activity_name_en: Test
owner: a
reviewer: b
defaults:
  connection: oracle_whouse
  frequency: monthly
"""

INDICATOR = """/*---
indicator_id: RI_05_0001
name_mn: Тест үзүүлэлт
description: тест
status: IN_PROGRESS
version: 0.1.0
weight: 2.5%
scale_text: "1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош"
min_rows: 10
max_change_pct: {pct: 25}
source_check: |
  SELECT COUNT(*) FROM x WHERE d = :p_report_date
---*/
SELECT 'SOL' AS ENTITY_LEVEL, '101' AS ENTITY_ID, 2 AS VALUE FROM dual WHERE :p_report_date IS NOT NULL
"""


def make(tmp_path, files: dict):
    act = tmp_path / "act_05_test"
    act.mkdir(parents=True)
    (act / "activity.yaml").write_text(ACTIVITY, encoding="utf-8")
    for name, text in files.items():
        (act / name).write_text(text, encoding="utf-8")
    return load_catalog(tmp_path)


def test_split_front_matter():
    meta, body = split_front_matter(INDICATOR)
    assert "indicator_id: RI_05_0001" in meta
    assert body.strip().startswith("SELECT 'SOL'")
    assert split_front_matter("SELECT 1") == (None, "SELECT 1")


def test_load_indicator_inherits_defaults(tmp_path):
    cat = make(tmp_path, {"ri_05_0001.sql": INDICATOR})
    ind = cat.indicators["RI_05_0001"]
    assert not ind.errors and not cat.errors
    assert ind.connection == "oracle_whouse" and ind.frequency == "monthly"
    assert ind.mode == "sql" and ind.weight == 2.5 and ind.min_rows == 10
    assert ind.scale["unit"] == "percent" and not ind.scale_error
    assert ind.max_change_pct == {"pct": 25.0}
    assert "COUNT(*)" in ind.source_check
    assert "indicator_id" not in ind.read_sql()          # тохиргоо SQL-д орохгүй


def test_wrong_id_and_stray_files(tmp_path):
    cat = make(tmp_path, {"ri_05_0002.sql": INDICATOR, "ri_05_0003.yaml": "x: 1"})
    assert "RI_05_0002" not in cat.indicators
    assert any("RI_05_0002 байх ёстой" in e for e in cat.errors)
    assert any("ri_05_0003.yaml" in e for e in cat.errors)


def test_sql_from(tmp_path):
    reuse = """/*---
indicator_id: RI_05_0002
name_mn: Давталт
description: d
sql_from: RI_05_0001
params: {p_segment: RETAIL}
status: TODO
version: 0.1.0
---*/
"""
    cat = make(tmp_path, {"ri_05_0001.sql": INDICATOR, "ri_05_0002.sql": reuse})
    ind = cat.indicators["RI_05_0002"]
    assert not ind.errors
    assert ind.params == {"p_segment": "RETAIL"}
    assert ind.read_sql().strip().startswith("SELECT 'SOL'")


def test_invalid_options(tmp_path):
    bad = INDICATOR.replace("min_rows: 10", "min_rows: -1").replace("{pct: 25}", "{x: 1}")
    cat = make(tmp_path, {"ri_05_0001.sql": bad})
    errs = " ".join(cat.indicators["RI_05_0001"].errors)
    assert "min_rows" in errs and "max_change_pct" in errs


SHARED = """/*---
indicator_id: SH_001
name_mn: Ажилтны тогтвортой байдал
status: IN_PROGRESS
version: 0.1.0
connection: oracle_ra
frequency: quarterly
---*/
SELECT 'SOL' AS ENTITY_LEVEL, SOL_ID AS ENTITY_ID, 1 AS NUMERATOR, 2 AS DENOMINATOR, 0.5 AS VALUE FROM x
"""


def test_shared_and_manual_modes(tmp_path):
    (tmp_path / "_shared").mkdir()
    (tmp_path / "_shared" / "sh_001.sql").write_text(SHARED, encoding="utf-8")
    shared = """/*---
indicator_id: RI_05_0003
name_mn: Ажилтны тогтвортой байдал
calc: SH_001
weight: 3
scale_text: "1-10%-аас доош | 3-10%-20% | 5-20%-аас дээш"
status: IN_PROGRESS
version: 0.1.0
---*/
"""
    manual = """/*---
indicator_id: RI_05_0004
name_mn: Action plan биелэлт
manual: true
weight: 1
scale_text: "1-Тийм | 5-Үгүй"
status: TODO
version: 0.1.0
---*/
"""
    bad = shared.replace("RI_05_0003", "RI_05_0005").replace("SH_001", "SH_009") + "SELECT 1 FROM dual\n"
    cat = make(tmp_path, {"ri_05_0003.sql": shared, "ri_05_0004.sql": manual, "ri_05_0005.sql": bad})
    assert "SH_001" in cat.calcs and cat.calcs["SH_001"].is_calc
    s = cat.indicators["RI_05_0003"]
    assert s.mode == "shared" and s.calc_id == "SH_001" and s.connection == "oracle_ra" and not s.errors
    m = cat.indicators["RI_05_0004"]
    assert m.mode == "manual" and m.scale["type"] == "string" and not m.errors
    errs = " ".join(cat.indicators["RI_05_0005"].errors)
    assert "SH_009" in errs and "SQL бичихгүй" in errs


def test_resolve_activity_by_branch(tmp_path):
    cat = make(tmp_path, {"ri_05_0001.sql": INDICATOR})
    cat.activities["ACT_05"].branch_id = "1162"
    for key in ("1162", "ACT_05", "act_05", "05", "5"):
        assert cat.resolve_activity(key).activity_id == "ACT_05"
    assert [i.indicator_id for i in cat.by_branch("1162")] == ["RI_05_0001"]
    import pytest
    with pytest.raises(ValueError):
        cat.resolve_activity("999")


def test_period_from_master_text_and_calc(tmp_path):
    """period: бичээгүй бол master-ийн "Хамрах хугацаа"-аас; хоосон бол нийтлэг тооцооллынхоос."""
    from ri_runner.metadata import infer_period
    assert infer_period("Сүүлийн 1 жил") == "last_year"
    assert infer_period("Аудит орсносс хойш хугацаанд улирлын дунджаар") == "since_audit"      # үсгийн алдаатай
    assert infer_period("Хамгийн сүүлд авсан шалгалтаар") == "latest"
    assert infer_period("Тайлант хугацаагаар") == infer_period("") == "report"
    (tmp_path / "_shared").mkdir()
    (tmp_path / "_shared" / "sh_001.sql").write_text(SHARED.replace("frequency: quarterly",
                                                                    "frequency: quarterly\nperiod: since_audit"),
                                                       encoding="utf-8")
    head = "/*---\nindicator_id: {}\nname_mn: x\ncalc: SH_001\nstatus: TODO\nversion: 0.1.0\n{}---*/\n"
    cat = make(tmp_path, {"ri_05_0001.sql": head.format("RI_05_0001", "period_text: Сүүлийн 1 жил\n"),
                          "ri_05_0002.sql": head.format("RI_05_0002", ""),
                          "ri_05_0003.sql": head.format("RI_05_0003", "period: latest\n")})
    assert [cat.indicators[f"RI_05_000{n}"].period for n in (1, 2, 3)] == ["last_year", "since_audit", "latest"]


def test_env_params_override(tmp_path):
    from ri_runner.metadata import apply_env_params
    reuse = INDICATOR.replace("min_rows: 10", "params: {p_pkeys: TODO}")
    cat = make(tmp_path, {"ri_05_0001.sql": reuse})
    cfg = type("Cfg", (), {"env": "local", "raw": {"params": {"ri_05_0001": {"p_pkeys": "10001"}, "RI_05_0099": {}}}})
    apply_env_params(cat, cfg)
    assert cat.indicators["RI_05_0001"].params == {"p_pkeys": "10001"}
    assert any("RI_05_0099" in e for e in cat.errors)
