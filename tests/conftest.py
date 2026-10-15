"""pytest: ri_runner-ийг import хийхэд project root-ыг path-д нэмнэ.

Ажиллуулах:
    pip install -r requirements-dev.txt
    pytest                       # unit (DB-гүй, ~1 сек)
    pytest -m local              # Docker Oracle + ClickHouse дээр demo DB-ийн бүтэн урсгал (tests/local/setup.sh)
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def make_ind(tmp_path):
    """Нэг үзүүлэлт (Indicator) — файлтай (sql_version тооцогдоно)."""
    from ri_runner.metadata import Indicator

    def make(**kw):
        iid = kw.pop("indicator_id", "RI_05_0001")
        folder = tmp_path / "act_05_test"
        folder.mkdir(exist_ok=True)
        (folder / f"{iid.lower()}.sql").write_text(f"/*---\nindicator_id: {iid}\n---*/\nSELECT 1 AS VALUE FROM dual\n",
                                                   encoding="utf-8")
        base = dict(indicator_id=iid, activity_id="ACT_05", folder=folder, name_mn="Тест", name_en="", description="",
                    owner="", reviewer="", connection="oracle_whouse", frequency="quarterly", execution_order=100,
                    dependencies=[], enabled=True, timeout_seconds=0, status="IN_PROGRESS", version="0.1.0",
                    complexity="simple", test_dates=[], empty_source="warn", example=False)
        base.update(kw)
        return Indicator(**base)
    return make
