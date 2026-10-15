"""Oracle (whouse)-д SQL ажиллуулж хүснэгтээр хэвлэнэ (sqlplus-ийн оронд, зөвхөн уншина).

    python tests/local/ora_query.py                                  # shell: whouse> SQL; (гарах: exit)
    python tests/local/ora_query.py "SELECT * FROM COREMIS.MAIN"     # нэг query
    python tests/local/ora_query.py --env dev "SELECT ..."           # dev Oracle (.env-ийн DEV_ORACLE_WHOUSE)

Shell-ийн товч тушаал:  tables  — whouse-ийн хүснэгт, мөрийн тоо;  desc COREMIS.MAIN  — баганууд.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ch_query import print_table  # noqa: E402
from ri_runner.config import EnvConfig  # noqa: E402
from ri_runner.db import connect  # noqa: E402

CONNECTION = "oracle_whouse"
LIMIT = 200


def owners(cfg: EnvConfig) -> str:
    return ", ".join(f"'{str(s).upper()}'" for s in sorted(set(cfg.schemas.values())))


def run(conn, cfg: EnvConfig, text: str) -> None:
    sql = text.strip().rstrip(";").strip()
    if not sql:
        return
    words = sql.split()
    if words[0].lower() == "tables":
        sql = (f"SELECT owner || '.' || table_name AS table_name, num_rows FROM all_tables "
               f"WHERE owner IN ({owners(cfg)}) ORDER BY 1")
        _, rows = conn.query(sql, {})
        rows = [(name, conn.query(f"SELECT COUNT(*) FROM {name}", {})[1][0][0]) for name, _ in rows]
        print_table(["TABLE_NAME", "ROWS"], rows)
        return
    if words[0].lower() == "desc" and len(words) == 2 and "." in words[1]:
        owner, table = words[1].upper().split(".", 1)
        sql = (f"SELECT column_name, data_type, data_length, nullable FROM all_tab_columns "
               f"WHERE owner = '{owner}' AND table_name = '{table}' ORDER BY column_id")
    cols, rows = conn.query(sql, {})
    if len(rows) > LIMIT:
        print(f"(эхний {LIMIT} мөр, нийт {len(rows)})")
    print_table(cols, rows[:LIMIT])


def shell(conn, cfg: EnvConfig, where: str) -> None:
    try:
        import readline  # noqa: F401 — сумаар өмнөх тушаал
    except ImportError:
        pass
    print(f"Oracle {where}. SQL-ээ ';'-ээр төгсгөнө. tables · desc SCHEMA.TABLE · exit")
    buf: list[str] = []
    while True:
        try:
            line = input("whouse> " if not buf else "   ...> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not buf and line.strip().lower() in ("exit", "quit", "\\q"):
            return
        buf.append(line)
        text = "\n".join(buf).strip()
        first = text.split()[0].lower() if text else ""
        if text.endswith(";") or first in ("tables", "desc"):
            buf = []
            try:
                run(conn, cfg, text)
            except Exception as exc:  # noqa: BLE001 — алдаатай SQL shell-ийг зогсоохгүй
                print(f"Алдаа: {str(exc).splitlines()[0]}")


def main() -> None:
    args = sys.argv[1:]
    env = "local"
    if args[:1] == ["--env"]:
        env, args = args[1], args[2:]
    cfg = EnvConfig(env)
    where = cfg.connection_settings(CONNECTION).get("connect_string", "").rsplit("@", 1)[-1]
    with connect(cfg, CONNECTION) as conn:
        if args:
            run(conn, cfg, " ".join(args))
        else:
            shell(conn, cfg, where)


if __name__ == "__main__":
    main()
