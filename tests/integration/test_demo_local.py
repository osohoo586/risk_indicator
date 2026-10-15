"""Docker Oracle + ClickHouse (--env local) дээр стандарт банкны demo DB-ийн бүтэн урсгал: pytest -m local

tests/local/demo_check.py-г ажиллуулна: seed → run (35 үйл ажиллагаа, Q2, Q3) → гарын үнэлгээ → verify →
эталон (Python) ↔ ClickHouse → хамгаалалт, давтан ажиллуулалт, бүтцийн өөрчлөлт, auto, алдааны тохиолдлууд.
Docker асаагүй бол (./tests/local/setup.sh хийгээгүй) skip. Үр дүн risk_assessment_local-д (dev, prod-д хүрэхгүй).
"""
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.local


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False


def test_demo_bank_end_to_end():
    if not (_port_open(1521) and _port_open(8123)):
        pytest.skip("Docker Oracle (1521) / ClickHouse (8123) алга — ./tests/local/setup.sh")
    out = subprocess.run([sys.executable, "tests/local/demo_check.py"], cwd=ROOT, capture_output=True, text=True,
                         timeout=1800)
    assert out.returncode == 0, out.stdout[-4000:] + out.stderr[-2000:]
    assert "АМЖИЛТТАЙ" in out.stdout
