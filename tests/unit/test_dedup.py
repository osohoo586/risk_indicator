"""Давхардлын дүрэм (dedup.decide) ба activity.yaml `shared:` manifest (DB-гүй)."""
import pytest

from ri_runner import dedup, tools
from ri_runner.cli import ids_from_paths
from ri_runner.metadata import load_catalog
from tests.unit.test_metadata import ACTIVITY, SHARED

GOOD = "1-96.1%-аас дээш\n3-90.1%-96%\n5-90%-с доош"


def row(iid, g, name="Action plan биелэлт", **kw):
    r = {"iid": iid, "g": g, "n": int(iid[-4:]), "indicator": name, "score_type": "Үйл ажиллагаа",
         "scale": GOOD, "source_system": "", "required_info": "", "method": "KPI-аар", "period_text":
         "Тайлант хугацаагаар", "automatable": "Тийм", "data_mapping": ""}
    r.update(kw)
    return r


def test_norm_key_merges_spelling_variants():
    assert dedup.norm_key("Action plan  биелэлт.") == dedup.norm_key("action plan биелэлт")
    assert dedup.norm_key("«Ёс зүйн» зөрчил") == dedup.norm_key("ес зүйн зөрчил")
    assert dedup.norm_key("Харилцагчийн тоо - УБ") == dedup.norm_key("Харилцагчийн тоо-УБ")
    assert dedup.norm_key("Харилцагчийн тоо-УБ") != dedup.norm_key("Харилцагчийн тоо-ОН")


def test_decide_one_definition_per_name_and_rules():
    rows = [
        row("RI_01_0001", 1),
        row("RI_02_0010", 2, name="action plan биелэлт."),                   # бичиглэл өөр → ижил
        row("RI_03_0020", 3, scale="s-Дунд\nТийм"),                          # master эвдэрсэн
        row("RI_04_0030", 4, scale=GOOD + "\n0-Үнэлэхгүй"),                  # илүү мөр
        row("RI_05_0040", 5, scale="1-99%-аас дээш\n3-95%-99%\n5-95%-с доош"),  # санаатай өөр
        row("RI_06_0050", 6, period_text=""),                                # хугацаа хоосон
        row("RI_07_0060", 7, period_text="Сүүлийн 1 жил"),                   # хугацаа өөр
        row("RI_08_0070", 8, method="ЖДБГ-ын KPI-аар", automatable=""),      # аргачлал, автомат өөр
        row("RI_09_0080", 9, name="Зөвхөн энэ үйл ажиллагааных"),
    ]
    defs = {d.name: d for d in dedup.decide(rows)}
    assert len(defs) == 2
    common = defs["Action plan биелэлт"]
    assert common.is_common and common.groups == [1, 2, 3, 4, 5, 6, 7, 8]
    assert common.fields["scale"] == GOOD and common.fields["period_text"] == "Тайлант хугацаагаар"
    dec = common.decisions
    assert not dec["RI_01_0001"].overrides and not dec["RI_02_0010"].overrides
    assert not dec["RI_03_0020"].overrides and "задрахгүй" in dec["RI_03_0020"].notes[0]
    assert not dec["RI_04_0030"].overrides and "илүү мөр" in dec["RI_04_0030"].notes[0]
    assert dec["RI_05_0040"].overrides == {"scale_text": "1-99%-аас дээш\n3-95%-99%\n5-95%-с доош"}
    assert not dec["RI_06_0050"].overrides and "хоосон" in dec["RI_06_0050"].notes[0]
    assert dec["RI_07_0060"].overrides == {"period_text": "Сүүлийн 1 жил"}
    assert dec["RI_08_0070"].overrides == {"method": "ЖДБГ-ын KPI-аар"}
    assert any("автоматжуулах" in n for n in dec["RI_08_0070"].notes)
    single = defs["Зөвхөн энэ үйл ажиллагааных"]
    assert not single.is_common and not single.decisions["RI_09_0080"].notes


def test_families_are_reported_not_merged():
    assert dedup.base_of("нийт ритэйл харилцагчийн тоо-уб") == ("нийт ритэйл харилцагчийн тоо", "уб")
    rows = [row("RI_01_0001", 1, name="Нийт ритэйл харилцагчийн тоо-УБ"),
            row("RI_01_0002", 1, name="Нийт ритэйл харилцагчийн тоо-ОН")]
    defs = dedup.decide(rows)
    assert len(defs) == 2                                             # утга нь өөр → тусдаа
    fams = dedup.families(defs)
    assert len(fams) == 1 and len(fams[0][1]) == 2


MANIFEST = ACTIVITY + """
shared:
  - {id: RI_05_0101, def: SH_001, weight: 1.5}
  - id: RI_05_0102
    def: SH_001
    weight: 2
    scale_text: "1-10%-аас доош | 3-10%-20% | 5-20%-аас дээш"
    period_text: Сүүлийн 1 жил
    params: {p_region: ОН}
"""


def make_manifest(tmp_path, manifest=MANIFEST, files=None):
    (tmp_path / "_shared").mkdir()
    (tmp_path / "_shared" / "sh_001.sql").write_text(
        SHARED.replace("frequency: quarterly", "frequency: quarterly\nscale_text: \"1-0.9-өөс дээш | 5-0.9 ба доош\""),
        encoding="utf-8")
    act = tmp_path / "act_05_test"
    act.mkdir()
    (act / "activity.yaml").write_text(manifest, encoding="utf-8")
    for name, text in (files or {}).items():
        (act / name).write_text(text, encoding="utf-8")
    return load_catalog(tmp_path)


def test_manifest_instances_take_definition_and_overrides(tmp_path):
    cat = make_manifest(tmp_path)
    assert not cat.errors
    a, b = cat.indicators["RI_05_0101"], cat.indicators["RI_05_0102"]
    for ind in (a, b):
        assert ind.mode == "shared" and ind.calc == "SH_001" and ind.def_id == "SH_001"
        assert ind.activity_id == "ACT_05" and not ind.errors
        assert ind.file_name.endswith("sh_001.sql")                     # ri_result.file_name = тодорхойлолт
    assert a.weight == 1.5 and a.scale_text == cat.calcs["SH_001"].scale_text and a.period == "report"
    assert b.weight == 2 and "20%-аас дээш" in b.scale_text and not b.scale_error
    assert b.period == "last_year" and b.params == {"p_region": "ОН"}
    assert a.sql_version != b.sql_version                               # мөрийн зөрүү → өөр хувилбар
    assert ids_from_paths(cat, [str(tmp_path / "act_05_test" / "activity.yaml")]) == ["RI_05_0101", "RI_05_0102"]
    assert ids_from_paths(cat, [str(tmp_path / "_shared" / "sh_001.sql")]) == ["RI_05_0101", "RI_05_0102"]


@pytest.mark.parametrize("entry, message", [
    ("{id: RI_05_0101, def: SH_001}", "weight заавал"),
    ("{id: RI_05_0101, def: SH_001, weight: 1, wieght: 2}", "мэдэгдэхгүй түлхүүр"),
    ("{id: RI_05_0101, def: SH_009, weight: 1}", "олдсонгүй"),
    ("{id: RI_06_0101, def: SH_001, weight: 1}", "RI_05_NNNN"),
    ("{id: RI_05_0001, def: SH_001, weight: 1}", "давхардсан"),
    ("{id: RI_05_0101, def: SH_001, weight: 1, period: someday}", "period"),
])
def test_manifest_errors(tmp_path, entry, message):
    own = ("/*---\nindicator_id: RI_05_0001\nname_mn: Өөр\nmanual: true\nstatus: TODO\nversion: 0.1.0\n---*/\n")
    cat = make_manifest(tmp_path, ACTIVITY + f"\nshared:\n  - {entry}\n", {"ri_05_0001.sql": own})
    errors = cat.errors + [e for i in cat.indicators.values() for e in i.errors]
    assert any(message in e for e in errors), errors


def test_status_without_new_status_shows_where(capsys):
    assert tools.describe("RI_40_1545") == 0
    out = capsys.readouterr().out
    assert "activities/act_40_human_resources/activity.yaml" in out and "activities/_shared/sh_007.sql" in out
    assert tools.describe("SH_007") == 0
    assert "35 үйл ажиллагаа" in capsys.readouterr().out
    assert tools.describe("RI_99_9999") == 2
