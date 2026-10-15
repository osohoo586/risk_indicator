"""Орчны бүх DB-г харуулна: source (Oracle / ClickHouse) хүснэгт, мөрийн тоо, procedure, үр дүнгийн хүснэгт.

    python tests/local/show_dbs.py              # --env local (docker Oracle + ClickHouse)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ri_runner.config import EnvConfig  # noqa: E402
from ri_runner.db import connect  # noqa: E402


def line(name: str, value) -> None:
    print(f"    {name:<44} {f'{value:,}' if isinstance(value, int) else value}")


def show_oracle(cfg: EnvConfig, name: str) -> None:
    owners = sorted({str(s).upper() for s in cfg.schemas.values()})
    with connect(cfg, name) as conn:
        _, tables = conn.query("SELECT owner, table_name FROM all_tables WHERE owner IN ("
                               + ", ".join(f"'{o}'" for o in owners) + ") ORDER BY 1, 2", {})
        for owner, table in tables:
            line(f"{owner}.{table}", int(conn.query(f"SELECT COUNT(*) FROM {owner}.{table}", {})[1][0][0]))
        _, objs = conn.query("SELECT owner, object_name, object_type, status FROM all_objects WHERE owner IN ("
                             + ", ".join(f"'{o}'" for o in owners) + ") AND object_type IN ('PACKAGE', 'PROCEDURE', "
                             "'FUNCTION') ORDER BY 1, 2", {})
        for owner, obj, otype, status in objs:
            line(f"{owner}.{obj}", f"{otype.lower()} ({status})")


def show_clickhouse(cfg: EnvConfig, name: str, database: str) -> None:
    with connect(cfg, name) as conn:
        _, tables = conn.query("SELECT name, engine FROM system.tables WHERE database = {d:String} ORDER BY name",
                               {"d": database})
        if not tables:
            line(database, "алга (setup.sh / init-db хийгээгүй)")
        for table, engine in tables:
            count = conn.query(f"SELECT count() FROM `{database}`.`{table}`", {})[1][0][0]
            line(f"{database}.{table}", f"{count:,}" + ("  (view: сүүлийн утга)" if engine == "View" else ""))


def main() -> None:
    env = sys.argv[sys.argv.index("--env") + 1] if "--env" in sys.argv else "local"
    cfg = EnvConfig(env)
    print(f"Орчин: {env} (config/{env}.yaml)")
    groups: dict[tuple, list[str]] = {}
    for name, raw in cfg.connections.items():
        s = cfg.connection_settings(name)
        where = (s.get("connect_string", "").rsplit("@", 1)[-1] if s["type"] == "oracle" else
                 f"{s.get('host')}:{s.get('port')}")
        key = (s["type"], where, s.get("database", ""))
        groups.setdefault(key, []).append(name)

    for (ctype, where, database), names in groups.items():
        role = "үр дүн" if cfg.result_connection in names else "source"
        title = {"oracle": "Oracle", "clickhouse": "ClickHouse"}[ctype]
        print(f"\n━━ {title} [{role}]  {where}{' / ' + database if database else ''}   connection: {', '.join(names)}")
        try:
            if ctype == "oracle":
                show_oracle(cfg, names[0])
            else:
                show_clickhouse(cfg, names[0], database)
        except Exception as exc:  # noqa: BLE001
            line("холбогдсонгүй", str(exc).splitlines()[0][:100])

    try:
        with connect(cfg, cfg.result_connection) as ch:
            cols = ch.table_column_types(cfg.result_db, "ri_result")
            if cols:
                print(f"\n{cfg.result_db}.ri_result-ийн баганууд:")
                print("    " + ", ".join(f"{c} {t}" for c, t in cols.items()))
    except Exception:  # noqa: BLE001 — дээр холболтын алдааг харуулсан
        pass


if __name__ == "__main__":
    main()
