"""Шинэ activity болон үзүүлэлтийг загвараас үүсгэх."""
import datetime as dt
import re

from .config import ACTIVITIES_DIR, TEMPLATES_DIR, known_connections
from .metadata import load_catalog

SLUG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def _render(template: str, values: dict) -> str:
    text = (TEMPLATES_DIR / template).read_text(encoding="utf-8")
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


def new_activity(number: int, slug: str, name_mn: str, name_en: str, owner: str,
                 reviewer: str, connection: str, frequency: str):
    if not 1 <= number <= 99:
        raise ValueError("Activity дугаар 1–99")
    if not SLUG_RE.match(slug):
        raise ValueError("slug нь англи, lowercase snake_case (жнь: credit_risk)")
    if owner == reviewer:
        raise ValueError("owner, reviewer өөр хүн байх ёстой")
    act_id = f"ACT_{number:02d}"
    existing = [p for p in ACTIVITIES_DIR.glob(f"act_{number:02d}_*") if p.is_dir()]
    if existing:
        raise ValueError(f"{act_id} аль хэдийн байна: {existing[0].name}")
    conns = known_connections()
    if conns and connection not in conns:
        raise ValueError(f"connection '{connection}' config/dev.yaml-д алга ({', '.join(conns)})")
    folder = ACTIVITIES_DIR / f"act_{number:02d}_{slug}"
    folder.mkdir(parents=True)
    (folder / "activity.yaml").write_text(_render("activity.yaml.tmpl", {
        "activity_id": act_id, "name_mn": name_mn, "name_en": name_en, "owner": owner,
        "reviewer": reviewer, "connection": connection, "frequency": frequency,
    }), encoding="utf-8")
    return folder


def new_indicator(activity_id: str, name_mn: str, name_en: str, connection: str | None,
                  frequency: str | None, complexity: str, count: int = 1,
                  number: int | None = None, catalog=None) -> list:
    cat = catalog or load_catalog()
    activity_id = activity_id.upper()
    act = cat.activities.get(activity_id)
    if act is None:
        raise ValueError(f"{activity_id} олдсонгүй. Эхлээд: python ri.py new-activity ...")
    connection = connection or act.defaults.get("connection")
    frequency = frequency or act.defaults.get("frequency") or "monthly"
    conns = known_connections()
    conn_type = conns.get(connection, "oracle")

    nn = activity_id[-2:]
    used = [int(p.stem[-4:]) for p in act.folder.glob(f"ri_{nn}_[0-9][0-9][0-9][0-9].sql")]
    # --number = master-ийн № (1–8999). Өгөхгүй бол master-д байхгүй нэмэлт үзүүлэлт: 9001, 9002, ...
    nxt = max([n for n in used if n >= 9000], default=9000) + 1
    if number is not None:
        if not 1 <= number <= 8999:
            raise ValueError("--number нь master-ийн № (1–8999)")
        taken = [n for n in range(number, number + count) if n in used]
        if taken:
            raise ValueError(f"RI_{nn}_{taken[0]:04d} аль хэдийн байна")
        nxt = number
    created = []
    for k in range(count):
        num = nxt + k
        if num > 9999:
            raise ValueError("Дугаар 9999-өөс хэтэрлээ")
        ind_id = f"RI_{nn}_{num:04d}"
        values = {
            "indicator_id": ind_id, "table": ind_id.lower(), "activity_id": activity_id,
            "name_mn": name_mn if count == 1 else f"{name_mn} {k + 1}",
            "name_en": name_en if count == 1 else f"{name_en} {k + 1}",
            "connection": connection, "frequency": frequency, "complexity": complexity,
            "owner": act.owner, "reviewer": act.reviewer, "today": dt.date.today().isoformat(),
        }
        stem = ind_id.lower()
        sql_tmpl = "indicator_clickhouse.sql.tmpl" if conn_type == "clickhouse" else "indicator_oracle.sql.tmpl"
        (act.folder / f"{stem}.sql").write_text(_render(sql_tmpl, values), encoding="utf-8")
        created.append(act.folder / f"{stem}.sql")
    return created
