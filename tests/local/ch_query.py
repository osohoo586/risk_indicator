"""ClickHouse-д SQL ажиллуулж хүснэгтээр хэвлэнэ (орчны үр дүнгийн connection).

    python tests/local/ch_query.py "SELECT * FROM risk_assessment_local.v_risk_indicators LIMIT 5"
    python tests/local/ch_query.py --env dev "SELECT count() FROM risk_assessment.ri_result"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ri_runner.config import EnvConfig  # noqa: E402
from ri_runner.db import connect  # noqa: E402


def fmt(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, float):
        return f"{v:.4f}".rstrip("0").rstrip(".")
    return str(v)


def print_table(cols, rows) -> None:
    cells = [[fmt(v) for v in r] for r in rows]
    widths = [max([len(c.lower())] + [len(r[i]) for r in cells]) for i, c in enumerate(cols)]
    print("  ".join(c.lower().ljust(w) for c, w in zip(cols, widths)))
    print("  ".join("-" * w for w in widths))
    for r in cells:
        print("  ".join(v.rjust(w) if v.replace(".", "").replace("-", "").isdigit() else v.ljust(w)
                        for v, w in zip(r, widths)))
    print(f"({len(rows)} мөр)")


def show(sql: str, env: str = "local") -> list:
    cfg = EnvConfig(env)
    with connect(cfg, cfg.result_connection) as conn:
        cols, rows = conn.query(sql, {})
    print_table(cols, rows)
    return rows


def main() -> None:
    args = sys.argv[1:]
    env = "local"
    if args[:1] == ["--env"]:
        env, args = args[1], args[2:]
    if not args:
        sys.exit(__doc__)
    show(" ".join(args), env)


if __name__ == "__main__":
    main()
