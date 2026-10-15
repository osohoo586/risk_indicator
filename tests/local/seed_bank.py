"""Стандарт банкны DEMO DB-г (tests/local/bank_demo.py) Docker Oracle + ClickHouse (--env local)-д ачаална.

    python tests/local/seed_bank.py

Oracle (FREEPDB1): COREMIS, FINACLE, ERP, CARDZONE, JIRA — NO AUTHENTICATION хэрэглэгч (зөвхөн хүснэгт эзэмшинэ),
PK / FK / CHECK constraint, хүснэгт бүр тайлбартай (DBeaver-т харагдана), FINACLE.RA_LOAN_PKG (хуучин procedure).
ClickHouse: cardzone_dwh.card_txn (CARDZONE.CARD_TXN-ийн DWH хуулбар, ClickHouse source-ийн жишээ).
Давтан ажиллуулахад эдгээр schema-г бүхэлд нь устгаад шинээр үүсгэнэ (бусад schema-д хүрэхгүй).
Мөн tests/local/demo/activity_map.csv (local-ийн BRANCHID, аудитын огноо)-г шинэчилнэ.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bank_demo  # noqa: E402
from ri_runner.config import EnvConfig  # noqa: E402
from ri_runner.db import connect  # noqa: E402

INDEXES = [
    "CREATE INDEX COREMIS.GL_REPORT_DATA_IX ON COREMIS.GL_REPORT_DATA (REPORTNO, TXNDATE)",
    "CREATE INDEX COREMIS.CUSTOMER_COMPLAINT_IX ON COREMIS.CUSTOMER_COMPLAINT (REG_DATE, SOLID)",
    "CREATE INDEX ERP.EMPLOYEE_HISTORY_IX ON ERP.EMPLOYEE_HISTORY (EMPLOYEE_ID, START_DATE)",
    "CREATE INDEX ERP.ERP_HR_TRAINING_IX ON ERP.ERP_HR_TRAINING (START_DATE)",
    "CREATE INDEX CARDZONE.CARD_TXN_IX ON CARDZONE.CARD_TXN (TXN_DATE)",
]


def _char_semantics(typ: str) -> str:
    return re.sub(r"VARCHAR2[(](\d+)[)]", r"VARCHAR2(\1 CHAR)", typ)


def input_size(oracledb, typ: str):
    """executemany-д баганын төрөл (эхний мөр NULL байхад буруу таахаас сэргийлнэ)."""
    base = typ.split()[0].upper()
    if base == "DATE":
        return oracledb.DB_TYPE_DATE
    if base.startswith("NUMBER"):
        return oracledb.DB_TYPE_NUMBER
    m = re.search(r"\((\d+)\)", base)
    return int(m.group(1)) * 4 if m else 4000          # UTF-8 кирилл: 1 тэмдэгт ≤ 4 байт


def load_oracle(cfg: EnvConfig, data: dict) -> list[str]:
    import oracledb
    out = []
    with connect(cfg, "oracle_whouse") as ora:
        cur = ora.conn.cursor()
        for schema in bank_demo.SCHEMAS:
            try:
                cur.execute(f"DROP USER {schema} CASCADE")
            except Exception as exc:  # noqa: BLE001 — ORA-01918: анх удаа
                if "ORA-01918" not in str(exc):
                    raise
            cur.execute(f"CREATE USER {schema} NO AUTHENTICATION DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS")
        for schema, tables in bank_demo.SCHEMAS.items():
            for name, (cols, constraints, comment) in tables.items():      # FK-ийн дарааллаар
                full = f"{schema}.{name}"
                # VARCHAR2(n CHAR): кирилл тэмдэгт 2 байт тул тэмдэгтээр хэмжинэ
                body = ",\n  ".join([f"{c} {_char_semantics(t)}" for c, t in cols] + constraints)
                cur.execute(f"CREATE TABLE {full} (\n  {body}\n)")
                cur.execute(f"COMMENT ON TABLE {full} IS '{comment.replace(chr(39), chr(39) * 2)}'")
                rows = data.get(full, [])
                if rows:
                    cur.setinputsizes(*[input_size(oracledb, t) for _, t in cols])
                    sql = f"INSERT INTO {full} VALUES ({', '.join(f':{k + 1}' for k in range(len(cols)))})"
                    for i in range(0, len(rows), 20000):
                        cur.executemany(sql, rows[i:i + 20000])
                ora.conn.commit()
                out.append(f"  {full:<36} {len(rows):>7} мөр")
        for sql in INDEXES:
            cur.execute(sql)
        for stmt in (s.strip() for s in bank_demo.FINACLE_PACKAGE.split("\n/\n")):
            if stmt:
                cur.execute(stmt)
        cur.execute("SELECT status FROM all_objects WHERE owner = 'FINACLE' AND object_name = 'RA_LOAN_PKG' "
                    "AND object_type = 'PACKAGE BODY'")
        status = cur.fetchone()[0]
        out.append(f"  FINACLE.RA_LOAN_PKG                  {status} (хуучин procedure: DECISION_SPEED → :rc)")
        if status != "VALID":
            sys.exit("FINACLE.RA_LOAN_PKG compile алдаатай")
    return out


def load_clickhouse(cfg: EnvConfig, data: dict) -> str:
    db = cfg.connection_settings("clickhouse_dwh")["database"]
    issue = data["_card_issue_sol"]
    rows = [[r[0], r[1], issue[r[1]], r[2], r[3], r[4], r[5], 1 if r[6] == "Y" else 0] for r in data["CARDZONE.CARD_TXN"]]
    with connect(cfg, "clickhouse_dwh") as ch:
        ch.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
        ch.execute(f"DROP TABLE IF EXISTS `{db}`.card_txn SYNC")
        ch.execute(bank_demo.CH_CARD_TXN.replace("{db}", f"`{db}`"))
        ch.insert(db, "card_txn", ["txn_id", "card_id", "issue_sol_id", "terminal_id", "txn_date", "amount", "channel",
                                   "is_fraud"], rows)
    return f"  ClickHouse {db}.card_txn{'':<14} {len(rows):>7} мөр (CARDZONE.CARD_TXN-ийн хуулбар)"


def main() -> None:
    cfg = EnvConfig("local")
    data = bank_demo.build()
    lines = load_oracle(cfg, data)
    lines.append(load_clickhouse(cfg, data))
    amap = bank_demo.write_activity_map()
    dsn = cfg.connection_settings("oracle_whouse")["connect_string"].rsplit("@", 1)[1]
    print(f"Oracle {dsn} — стандарт банкны DEMO DB (tests/local/bank_demo.py, seed {bank_demo.SEED}):")
    print("\n".join(lines))
    print(f"  {amap.relative_to(bank_demo.ROOT)} (local-ийн BRANCHID, аудитын огноо)")


if __name__ == "__main__":
    main()
