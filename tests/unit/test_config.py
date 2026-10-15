import pytest

from ri_runner.config import ConfigError, resolve_vars


def test_resolve_vars_default(monkeypatch):
    monkeypatch.delenv("RI_X_HOST", raising=False)
    assert resolve_vars({"host": "${RI_X_HOST:-localhost}", "port": "${RI_X_PORT:-}"}) == {"host": "localhost", "port": ""}
    monkeypatch.setenv("RI_X_HOST", "ch.bank")
    assert resolve_vars("${RI_X_HOST:-localhost}:8123") == "ch.bank:8123"       # хувьсагч байвал default-ийг дарна
    with pytest.raises(ConfigError):
        resolve_vars("${RI_X_MISSING}")                                        # default-гүй бол алдаа
