"""Оноо: DaHUB-ийн computeScoreFromScale-тай ижил дүрэм + master-ийн шатлалын текст задлах."""
import pytest

from ri_runner.scale import UNELEHGUI, compute_score, parse_scale_text, risk_level

NUM = {"type": "numeric", "numericRules": [
    {"min": None, "max": 10, "score": 1, "label": "<10"},
    {"min": 10, "max": 20, "score": 3, "label": "10–20"},
    {"min": 20, "max": None, "score": 5, "label": "20+"},
]}


@pytest.mark.parametrize("value,expected", [
    (9.99, 1), (10, 3), (19.99, 3), (20, 5),          # min ≤ x < max
    ("12,5", 3),                                       # таслалтай бутархай
])
def test_numeric_boundaries(value, expected):
    assert compute_score(NUM, value)[0] == expected


def test_no_match_is_unelehgui():
    scale = {"type": "numeric", "numericRules": [{"min": 0, "max": 10, "score": 2}]}
    assert compute_score(scale, 50) == (UNELEHGUI, "тодорхойлогдоогүй")


def test_score_zero_is_unelehgui():
    scale = {"type": "numeric", "numericRules": [{"min": 0, "max": 10, "score": 0, "label": "x"}]}
    assert compute_score(scale, 5)[0] == UNELEHGUI


def test_string_exact_and_contains():
    scale = {"type": "string", "stringRules": [
        {"values": ["Тийм"], "matchType": "exact", "score": 5},
        {"values": ["зөрчил"], "matchType": "contains", "score": 3},
    ]}
    assert compute_score(scale, " Тийм ")[0] == 5
    assert compute_score(scale, "Тийм биш")[0] == UNELEHGUI
    assert compute_score(scale, "2 зөрчил илэрсэн")[0] == 3


def test_null_policy():
    assert compute_score(NUM, None)[0] == UNELEHGUI
    assert compute_score({**NUM, "null_empty_score": "5"}, "")[0] == 5
    assert compute_score({**NUM, "null_empty_score": "1"}, None)[0] == 1


def test_manual_and_no_score_types():
    assert compute_score({"type": "manual"}, 5) == (None, None)
    assert compute_score({"type": "no_score"}, 5) == (None, None)
    assert compute_score(None, 5) == (None, None)


@pytest.mark.parametrize("total,level", [(3.5, "Өндөр"), (3.49, "Дунд"), (2.5, "Дунд"), (2.49, "Бага"),
                                         (None, "")])
def test_risk_level(total, level):
    assert risk_level(total) == level


def test_parse_master_percent_scale():
    scale, err = parse_scale_text("0-Үнэлэхгүй\n1-96.1%-аас дээш\n3-90.1%-96%\n5-90% - с доош")
    assert err is None and scale["unit"] == "percent"
    # утга харьцаагаар (0.9746) ирнэ → ×100
    assert compute_score(scale, 0.9746)[0] == 1
    assert compute_score(scale, 0.9605)[0] == 3
    assert compute_score(scale, 0.9005)[0] == 5
    assert compute_score(scale, 96.05, value_unit="percent")[0] == 3


def test_parse_pipe_separated():
    scale, err = parse_scale_text("1-96.1%-аас дээш | 3-90.1%-96% | 5-90% - с доош")
    assert err is None and compute_score(scale, 0.95)[0] == 3


def test_parse_categories_to_string_rules():
    scale, err = parse_scale_text("1-Тийм\n5-Үгүй")
    assert err is None and scale["type"] == "string"
    assert compute_score(scale, "Үгүй")[0] == 5


def test_parse_failure():
    scale, err = parse_scale_text("Хорооны шийдвэрээр")
    assert scale is None and err


def test_bare_fraction_in_percent_scale():
    # master: "1-1" = 100% (орон тоо бүрэн)
    scale, _ = parse_scale_text("0-Үнэлэхгүй\n1-1\n2-95%-99%\n3-90%-94%\n4-85%-89%\n5-85%-с доош")
    assert [compute_score(scale, v)[0] for v in (1.0, 0.97, 0.92, 0.87, 0.80)] == [1, 2, 3, 4, 5]
    # master: "4-0.05" = 5%
    scale, _ = parse_scale_text("5-5% түүнээс дээш\n4-0.05\n3-4-4.9%\n2-3-3.9%\n1-3%-аас бага")
    assert [compute_score(scale, v)[0] for v in (0.02, 0.035, 0.045, 0.06)] == [1, 2, 3, 5]


# ── Master-ийн бодит шатлалууд (35 үйл ажиллагаанд давтагддаг нийтлэг үзүүлэлтүүд) ──
MASTER = {
    "ажилласан жил (U хэлбэр)": ("0-Үнэлэхгүй\n1-1-2 жил\n2-2-3 жил\n3-3-4 жил\n4-4-5 жил\n5-0-1 жил and 5-с дээш жил",
                                [(0.5, 5), (1.0, 1), (1.5, 1), (2.0, 2), (4.5, 4), (5.0, 4), (6, 5), (None, UNELEHGUI)]),
    "эргэц %": ("0-Үнэлэхгүй\n1-10%-аас бага\n2-10%-12%\n3-13%-15%\n4-16%-19%\n5-20% болон түүнээс дээш",
                [(0.05, 1), (0.10, 2), (0.125, 2), (0.14, 3), (0.17, 4), (0.20, 5), (0.30, 5)]),
    "орон тоо (1-1 = 100%)": ("0-Үнэлэхгүй\n1-1\n2-95%-99%\n3-90%-94%\n4-85%-89%\n5-85%-с доош",
                               [(1.05, 1), (1.0, 1), (0.97, 2), (0.92, 3), (0.85, 4), (0.80, 5)]),
    "гомдол (0 = гараагүй, ДАГ)": ("0-Үнэлэхгүй /Гомдол гараагүй/\n2-ХҮГ-ын бүртгэлээр 2 хүртэл гомдол гарсан\n"
                                   "3-ХҮГ-ын бүртгэлээр 2-3 гомдол гарсан\n4-ХҮГ-ын бүртгэлээр 3-с дээш гомдол гарсан\n"
                                   "5-ДАГ-т гомдол ирж, шалгагдсан.",
                                   [(0, UNELEHGUI), (1, 2), (2.5, 3), (3, 3), (3.5, 4), ("ДАГ-т гомдол ирж, шалгагдсан.", 5)]),
    "ёс зүй (Тийм/Үгүй, тоогоор)": ("0-Үнэлэхгүй /Үгүй/\n5-Тийм", [(0, UNELEHGUI), (2, 5), ("Тийм", 5)]),
    "сургалтын цаг": ("1-16 цагаас дээш\n2-14-15.9 цаг\n3-12-13.9 цаг\n4-10-11.9 цаг\n5-10 доош цаг",
                      [(20, 1), (16, 1), (15, 2), (13.95, 3), (10, 4), (9.9, 5)]),
    "удирдах ажилтан (+ангилал)": ("0-Үнэлэхгүй\n1-1-2 жил\n2-2-3 жил\n3-3-3.5 жил\n4-3.5-4 жил\n"
                                   "5-0-1 жил and 4-с дээш жил/удирдлага байхгүй/Захирал нь өөр банкнаас томилогдсон.",
                                   [(0.5, 5), (1.5, 1), (3.7, 4), (4.0, 4), (5, 5), ("удирдлага байхгүй", 5)]),
    "улиралд (10-аас бага, 11-13)": ("1-Улиралд 10-аас бага\n2-Улиралд 11-13\n3-Улиралд 14-16\n4-Улиралд 17-20\n"
                                     "5-Улиралд 20-иос дээш", [(9, 1), (10, 2), (13, 2), (20, 4), (21, 5)]),
    "өдөр (цэг)": ("1-15 өдөрт\n2-16 өдөрт\n3-17 өдөрт\n4-18 өдөрт\n5-19-с дээш өдөрт. Судалгааны хурдыг хэмждэггүй.",
                   [(10, 1), (15.5, 1), (16, 2), (19, 5), (25, 5)]),
    "нэг мөрөнд": ("1-96.1%-аас дээш 3-90.1%-96% 5-90%-с доош", [(0.97, 1), (0.95, 3), (0.90, 5)]),
}


@pytest.mark.parametrize("name", list(MASTER))
def test_master_scales(name):
    text, cases = MASTER[name]
    scale, err = parse_scale_text(text)
    assert err is None, err
    assert [(v, compute_score(scale, v)[0]) for v, _ in cases] == cases
