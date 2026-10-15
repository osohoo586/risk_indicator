"""Орчны тохиргоо (config/<env>.yaml) болон .env унших."""
import os
import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(os.environ.get("RI_HOME", Path(__file__).resolve().parent.parent))
CONFIG_DIR = PROJECT_ROOT / "config"
ACTIVITIES_DIR = PROJECT_ROOT / "activities"
SHARED_DIR = PROJECT_ROOT / "shared"          # Олон үзүүлэлтэд давхцдаг SQL: {{shared.name}}
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DDL_DIR = PROJECT_ROOT / "ddl"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

ENVIRONMENTS = ("local", "dev", "test", "prod")    # local = Docker Oracle + ClickHouse (стандарт банкны demo DB)
LOCAL_ENVIRONMENTS = ("local",)                     # компьютер дээрх тест: нууц үгийн файл заавал биш
_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$#]*$")


class ConfigError(Exception):
    pass


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    """.env файлаас хувьсагч уншина. Аль хэдийн тохируулсан env хувьсагчийг дарахгүй."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def resolve_vars(value):
    """${VAR}-ийг env хувьсагчаар солино (connection нээх үед л дуудагдана). ${VAR:-утга}: хувьсагч алга бол утга."""
    if isinstance(value, dict):
        return {k: resolve_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_vars(v) for v in value]
    if isinstance(value, str):
        def repl(m):
            name, default = m.group(1), m.group(2)
            if name not in os.environ:
                if default is not None:
                    return default
                raise ConfigError(f"Env хувьсагч олдсонгүй: {name} (.env файлаа шалгана уу)")
            return os.environ[name]
        return _VAR_RE.sub(repl, value)
    return value


class EnvConfig:
    def __init__(self, env: str):
        if env not in ENVIRONMENTS:
            raise ConfigError(f"Орчин буруу: {env}. Боломжит: {', '.join(ENVIRONMENTS)}")
        path = CONFIG_DIR / f"{env}.yaml"
        if not path.exists():
            raise ConfigError(f"Config файл олдсонгүй: {path}")
        load_dotenv()
        self.env = env
        self.raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        # Үр дүн бичигдэх газар: ClickHouse database (ri_result, audit, history, view — store.py)
        result = self.raw.get("result") or {}
        self.result_connection = result.get("connection")
        self.result_db = result.get("database")
        if not self.result_connection or not self.result_db:
            raise ConfigError(f"{path}: result.connection, result.database заавал")
        if not IDENTIFIER_RE.match(str(self.result_db)):
            raise ConfigError(f"result.database буруу: {self.result_db}")

        self.connections: dict = self.raw.get("connections") or {}
        rtype = (self.connections.get(self.result_connection) or {}).get("type")
        if rtype != "clickhouse":
            raise ConfigError(f"{path}: result.connection ({self.result_connection}) нь clickhouse байх ёстой")
        self.schemas: dict = self.raw.get("schemas") or {}
        for alias, name in self.schemas.items():
            if not IDENTIFIER_RE.match(str(name)):
                raise ConfigError(f"schemas.{alias} буруу identifier: {name}")

        self.min_status = self.raw.get("min_status", "TODO")
        self.enforce_frequency = bool(self.raw.get("enforce_frequency", False))
        # Шалгалт (FAIL) унасан үр дүнг ч хүснэгтэд бичих эсэх: dev-д харж засахад true, prod-д false
        self.insert_on_validation_fail = bool(self.raw.get(
            "insert_on_validation_fail", self.raw.get("keep_on_validation_fail", True)))
        self.keep_on_validation_fail = self.insert_on_validation_fail
        # :p_branch_id-тай (салбар бүрээр ажилладаг) кодод салбарын жагсаалт гаргах SQL
        bl = self.raw.get("branch_list") or {}
        self.branch_list_connection = bl.get("connection")
        self.branch_list_shared = bl.get("shared", "branch_list")
        self.allow_clean = bool(self.raw.get("allow_clean", True))
        self.default_workers = int(self.raw.get("default_workers", 4))
        self.default_timeout = int(self.raw.get("default_timeout_seconds", 600))

    def connection_type(self, name: str) -> str:
        if name not in self.connections:
            raise ConfigError(f"Connection '{name}' config/{self.env}.yaml-д алга")
        return self.connections[name]["type"]

    def connection_settings(self, name: str) -> dict:
        if name not in self.connections:
            raise ConfigError(f"Connection '{name}' config/{self.env}.yaml-д алга")
        return resolve_vars(self.connections[name])


def load_period() -> dict:
    """config/period.yaml: {start_date, end_date} эсвэл {period}."""
    path = CONFIG_DIR / "period.yaml"
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {k: raw.get(k) for k in ("start_date", "end_date", "period") if raw.get(k) not in (None, "")}


def known_connections() -> dict:
    """Static шалгалтад: connection нэр → type (env хувьсагч шаардахгүй).

    dev.yaml-ийнх эхэлж, дараа нь бусад орчны connection.
    """
    out: dict = {}
    for name in ["dev", *[p.stem for p in sorted(CONFIG_DIR.glob("*.yaml")) if p.stem != "dev"]]:
        path = CONFIG_DIR / f"{name}.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None
        if isinstance(raw, dict):
            for k, v in (raw.get("connections") or {}).items():
                out.setdefault(k, (v or {}).get("type"))
    return out


DEFAULT_SCORE_GROUPS = {
    "score1": "Бизнесийн үйл ажиллагаа, үр дүн",
    "score2": "Хүний нөөц, бүтэц, зохицуулалт",
    "score3": "Аудитын үр дүн",
    "score4": "Мэдлэг, нууцлал, харилцагч",
    "score5": "Стратеги, зах зээл",
    "score6": "Аудиторын үнэлэмж",
}


def load_scoring(cfg=None) -> dict:
    """config/scoring.yaml (+ config/<env>.yaml-ийн scoring:) → {high, medium, groups}."""
    p = CONFIG_DIR / "scoring.yaml"
    conf = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    if cfg is not None:
        conf = {**conf, **(cfg.raw.get("scoring") or {})}
    groups = {**DEFAULT_SCORE_GROUPS, **{str(k).lower(): str(v) for k, v in (conf.get("groups") or {}).items()}}
    return {"high": float(conf.get("high", 3.5)), "medium": float(conf.get("medium", 2.5)), "groups": groups}
