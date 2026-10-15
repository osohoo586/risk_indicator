import pytest

from ri_runner.config import ConfigError
from ri_runner.sqltext import clean_trailing, oracle_binds_used, render_schemas, strip_comments_and_strings
from ri_runner.importer import find_columns, read_table, slugify
from ri_runner.tools import set_status_in_file


def test_oracle_binds_ignore_strings_and_comments():
    sql = "SELECT TO_CHAR(d, 'HH24:MI') -- :p_fake\nFROM t WHERE d = :p_report_date /* :p_x */"
    assert oracle_binds_used(sql) == {"p_report_date"}


def test_strip_comments_and_strings():
    assert ":p" not in strip_comments_and_strings("SELECT ':p' /* :p */ -- :p\n")


def test_render_schemas():
    assert render_schemas("FROM {{schema.coremis}}.T", {"coremis": "COREMIS"}) == "FROM COREMIS.T"
    with pytest.raises(ConfigError):
        render_schemas("FROM {{schema.nope}}.T", {"coremis": "COREMIS"})


def test_clean_trailing():
    assert clean_trailing("SELECT 1;\n\n") == "SELECT 1"


def test_set_status_only_in_front_matter(tmp_path):
    f = tmp_path / "ri_01_001.sql"
    f.write_text("/*---\nindicator_id: RI_01_001\nstatus: TODO   # тайлбар\n---*/\nSELECT 'status: TODO' AS X\n",
                 encoding="utf-8")
    assert set_status_in_file(f, "REVIEW") == "TODO"
    text = f.read_text(encoding="utf-8")
    assert "status: REVIEW   # тайлбар" in text and "'status: TODO'" in text


def test_slugify():
    assert slugify("Хүний нөөцийн үйл ажиллагаа") == "khunii_nootsiin_uil"
    assert slugify("Картын үйл ажиллагаа") == "kartyn_uil_ajillagaa"


def test_find_columns_master_header():
    head = ["Бүлэг", "№", "Үйл ажиллагаа", "Үйл ажиллагааны нэр (хуучин)", "Risk indicator",
            "Үнэлгээнд нөлөөлөх хувийн жин", "Мэдээлэл авах суваг", "Шаардлагатай мэдээлэл", "Үнэлэх аргачлал",
            "Хамрах хугацаа", "Score", "Scale", "Автоматжуулах боломжтой эсэх", "Data mapping ", "Хөгжүүлэлт"]
    cols = find_columns(head)
    assert cols == {"group": 0, "number": 1, "activity": 2, "activity_old": 3, "indicator": 4, "weight": 5,
                    "source_system": 6, "required_info": 7, "method": 8, "period_text": 9, "score_type": 10,
                    "scale": 11, "automatable": 12, "data_mapping": 13, "development": 14}
    assert find_columns(["a", "b", "c", "d", "e"])["indicator"] == 4


def test_read_tsv_with_xlsx_extension(tmp_path):
    p = tmp_path / "master.xlsx"
    p.write_text('Бүлэг\t№\tҮйл ажиллагаа\tRisk indicator\n1\t2\tA\t"x\ny"\n', encoding="utf-8")
    assert read_table(p) == [["Бүлэг", "№", "Үйл ажиллагаа", "Risk indicator"], ["1", "2", "A", "x\ny"]]


def test_import_update_master_block(tmp_path):
    """--update: зөвхөн master хэсэг (нэр, жин, шатлал …) шинэчлэгдэнэ, тооцоолол / SQL хэвээр."""
    from ri_runner.importer import ORDER, indicator_text, update_master
    r = {k: "" for k in ORDER}
    r.update(indicator="Эргэц", weight=1.5, score_type="score1", scale="1-10%-аас бага\n5-20%-аас дээш",
             period_text="Сүүлийн 1 жил", automatable="Тийм", iid="RI_40_1520")
    text = indicator_text("RI_40_1520", r, "sql", None)
    head, _, sql = text.partition("---*/")
    custom = head + "# ── Тооцоолол ──\nconnection: oracle_whouse\n---*/\nSELECT 1 AS VALUE FROM dual\n"
    path = tmp_path / "ri_40_1520.sql"
    path.write_text(custom, encoding="utf-8")
    assert update_master(path, r) == (None, [])                   # master өөрчлөгдөөгүй → хүрэхгүй
    new_text, changed = update_master(path, {**r, "weight": 2.0, "scale": "1-9%-аас бага\n5-20%-аас дээш"})
    assert changed == ["scale_text", "weight"]
    assert "weight: 2 " in new_text and "1-9%-аас бага" in new_text
    assert "connection: oracle_whouse" in new_text and new_text.endswith("SELECT 1 AS VALUE FROM dual\n")
