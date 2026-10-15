import pytest

from ri_runner.config import ConfigError, EnvConfig, read_csv, read_text_any, resolve_vars, vars_in
from ri_runner.metadata import load_catalog
from tests.unit.test_metadata import INDICATOR, make


def test_resolve_vars_default(monkeypatch):
    monkeypatch.delenv("RI_X_HOST", raising=False)
    assert resolve_vars({"host": "${RI_X_HOST:-localhost}", "port": "${RI_X_PORT:-}"}) == {"host": "localhost", "port": ""}
    monkeypatch.setenv("RI_X_HOST", "ch.bank")
    assert resolve_vars("${RI_X_HOST:-localhost}:8123") == "ch.bank:8123"       # хувьсагч байвал default-ийг дарна
    with pytest.raises(ConfigError):
        resolve_vars("${RI_X_MISSING}")                                        # default-гүй бол алдаа


def test_vars_in_lists_required_only():
    conn = {"host": "${DEV_CH_HOST}", "port": "${DEV_CH_PORT:-8123}", "user": "${DEV_CH_USER}", "secure": False}
    assert vars_in(conn) == ["DEV_CH_HOST", "DEV_CH_USER"]                  # default-тэй нь заавал биш


@pytest.mark.parametrize("env", ["dev", "test", "prod"])
def test_env_configs_use_only_env_vars_for_secrets(env):
    cfg = EnvConfig(env)                                  # нууц үгийн файлгүй ч config ачаалагдана (холболт нээх үед л)
    for name, conn in cfg.connections.items():
        secret = conn.get("connect_string") or conn.get("password")
        assert secret is None or str(secret).startswith("${"), f"{env}.{name}: нууц үг config-д бичигдсэн"


def test_read_csv_excel_on_windows(tmp_path):
    """Windows-ийн Excel: "CSV" нь cp1251 + ';' (ү, ө үсэггүй — Excel '?' болгоно), "CSV UTF-8" нь BOM-той."""
    ansi = tmp_path / "ansi.csv"
    ansi.write_bytes("GROUP_NO;MASTER_NAME;BRANCHID\r\n24;Карт;1028\r\n".encode("cp1251"))
    bom = tmp_path / "bom.csv"
    bom.write_bytes("GROUP_NO,MASTER_NAME,BRANCHID\r\n40,Хүний нөөц,1006\r\n".encode("utf-8-sig"))
    assert read_csv(ansi) == [{"GROUP_NO": "24", "MASTER_NAME": "Карт", "BRANCHID": "1028"}]
    assert read_csv(bom) == [{"GROUP_NO": "40", "MASTER_NAME": "Хүний нөөц", "BRANCHID": "1006"}]
    assert read_text_any(ansi).startswith("GROUP_NO;")


def test_sql_version_same_on_windows_and_linux(tmp_path):
    lf = make(tmp_path / "lf", {"ri_05_0001.sql": INDICATOR}).indicators["RI_05_0001"]
    crlf_root = tmp_path / "crlf"
    make(crlf_root, {})
    (crlf_root / "act_05_test" / "ri_05_0001.sql").write_bytes(INDICATOR.replace("\n", "\r\n").encode("utf-8"))
    crlf = load_catalog(crlf_root).indicators["RI_05_0001"]
    assert lf.sql_version == crlf.sql_version
