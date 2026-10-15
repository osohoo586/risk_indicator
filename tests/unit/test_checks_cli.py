"""Static шалгалт (shared/, давхардал, procedure блок) ба файл / folder-ийн замаар сонголт."""
import pytest

from ri_runner import checks
from ri_runner.cli import ids_from_paths
from tests.unit.test_metadata import INDICATOR, SHARED, make


@pytest.fixture
def shared(tmp_path, monkeypatch):
    root = tmp_path / "shared"
    (root / "org").mkdir(parents=True)
    (root / "org" / "units.sql").write_text("SELECT m.SOLID AS SOLID, m.BRANCHID AS BRANCHID FROM MAIN m")
    (root / "org" / "unused.sql").write_text("SELECT e.ID AS ID FROM E e")
    (root / "Bad-Name.sql").write_text("DELETE FROM X")
    for mod in ("ri_runner.checks", "ri_runner.sqltext"):
        monkeypatch.setattr(f"{mod}.SHARED_DIR", root)
    return root


def test_checks_shared_block_and_duplicates(tmp_path, shared):
    uses = INDICATOR.replace("FROM dual", "FROM {{shared.org.units}} u")
    missing = INDICATOR.replace("RI_05_0001", "RI_05_0002").replace("FROM dual", "FROM {{shared.nope}} u")
    block = INDICATOR.replace("RI_05_0001", "RI_05_0003").split("---*/")[0] + "---*/\nBEGIN PKG.P(:p_report_date); END;\n"
    same = uses.replace("RI_05_0001", "RI_05_0004")
    cat = make(tmp_path / "acts", {"ri_05_0001.sql": uses, "ri_05_0002.sql": missing, "ri_05_0003.sql": block,
                                   "ri_05_0004.sql": same})
    errors, warnings = checks.run_checks(cat)
    text = " | ".join(errors + warnings)
    assert "{{shared.nope}}" in text and ":rc (SYS_REFCURSOR)" in text
    assert "RI_05_0004: SQL нь RI_05_0001-тэй яг ижил" in text
    assert "shared/org/unused.sql: аль ч үзүүлэлт ашиглаагүй" in text
    assert "shared/Bad-Name.sql: нэр жижиг үсэг" in text
    assert not any("units.sql: аль ч" in w for w in warnings)
    assert "BRANCHID алга (ТОДРУУЛАХ)" in " ".join(warnings)          # тохиргоо — commit-ийг хаахгүй


def test_ids_from_paths(tmp_path):
    (tmp_path / "_shared").mkdir()
    (tmp_path / "_shared" / "sh_001.sql").write_text(SHARED, encoding="utf-8")
    user = ("/*---\nindicator_id: RI_05_0003\nname_mn: Нийтлэг\ncalc: SH_001\nstatus: TODO\nversion: 0.1.0\n---*/\n")
    other = INDICATOR.replace("RI_05_0001", "RI_05_0002").replace("2 AS VALUE", "3 AS VALUE")
    cat = make(tmp_path, {"ri_05_0001.sql": INDICATOR, "ri_05_0002.sql": other, "ri_05_0003.sql": user})
    folder = tmp_path / "act_05_test"
    assert ids_from_paths(cat, [str(folder / "ri_05_0002.sql")]) == ["RI_05_0002"]
    assert ids_from_paths(cat, [str(folder)]) == ["RI_05_0001", "RI_05_0002", "RI_05_0003"]
    assert ids_from_paths(cat, [str(tmp_path / "_shared" / "sh_001.sql")]) == ["RI_05_0003"]   # тооцооллын хэрэглэгч
    assert ids_from_paths(cat, [str(folder / "ri_05_0001.sql"), str(folder)])[0] == "RI_05_0001"  # давхардахгүй
    for bad in (str(folder / "activity.yaml"), str(tmp_path / "nope")):
        with pytest.raises(ValueError):
            ids_from_paths(cat, [bad])
