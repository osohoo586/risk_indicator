import pytest

from ri_runner.config import ConfigError, EnvConfig, resolve_vars, vars_in


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
