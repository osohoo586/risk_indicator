"""SQL текст боловсруулах: comment/string хасах, bind олох, schema/shared placeholder render."""
import re
from pathlib import Path

from .config import IDENTIFIER_RE, SHARED_DIR, ConfigError

_SCHEMA_RE = re.compile(r"\{\{\s*schema\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_SHARED_RE = re.compile(r"\{\{\s*shared\.([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*)\s*\}\}")
_BLOCK_RE = re.compile(r"^(BEGIN|DECLARE)\b", re.I)
_ORACLE_BIND_RE = re.compile(r"(?<![:\w]):([A-Za-z_][A-Za-z0-9_]*)")


def strip_comments_and_strings(sql: str) -> str:
    """Comment болон '...' string-ийг хоосон болгоно (lint, bind хайхад)."""
    out, i, n = [], 0, len(sql)
    while i < n:
        c = sql[i]
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            i = n if j == -1 else j
        elif sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            i = n if j == -1 else j + 2
            out.append(" ")
        elif c == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'" and j + 1 < n and sql[j + 1] == "'":
                    j += 2
                elif sql[j] == "'":
                    break
                else:
                    j += 1
            out.append("''")
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def split_statements(sql: str) -> list[str]:
    """Олон statement-тэй SQL файлыг `;`-аар хуваана (comment, '...' доторх `;`-ийг тооцохгүй).

    Зөвхөн comment-оос бүрдсэн хэсгийг алгасна.
    """
    out, start, i, n = [], 0, 0, len(sql)
    while i < n:
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            i = n if j == -1 else j
        elif sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            i = n if j == -1 else j + 2
        elif sql[i] == "'":
            j = i + 1
            while j < n and not (sql[j] == "'" and not sql.startswith("''", j)):
                j += 2 if sql.startswith("''", j) else 1
            i = j + 1
        elif sql[i] == ";":
            out.append(sql[start:i])
            start = i = i + 1
        else:
            i += 1
    out.append(sql[start:])
    return [s.strip() for s in out if strip_comments_and_strings(s).strip()]


def render_schemas(sql: str, schemas: dict) -> str:
    """{{ schema.alias }}-ийг config-ийн whitelist-ээс солино."""
    def repl(m):
        alias = m.group(1)
        if alias not in schemas:
            raise ConfigError(f"Schema alias '{alias}' config-ийн schemas-д алга")
        name = str(schemas[alias])
        if not IDENTIFIER_RE.match(name):
            raise ConfigError(f"Schema нэр буруу: {name}")
        return name
    return _SCHEMA_RE.sub(repl, sql)


def oracle_binds_used(sql: str) -> set[str]:
    return {m.lower() for m in _ORACLE_BIND_RE.findall(strip_comments_and_strings(sql))}


def is_plsql_block(sql: str) -> bool:
    """BEGIN ... END; / DECLARE ... — Oracle procedure дуудах блок (үр дүнг :rc cursor-оор буцаана)."""
    return bool(_BLOCK_RE.match(strip_comments_and_strings(sql).strip()))


def clean_trailing(sql: str) -> str:
    """Төгсгөлийн ; ба хоосон мөрийг хасна (Oracle driver SELECT-ийн ;-ийг хүлээж авдаггүй).

    PL/SQL блокийн `END;`-ийг хэвээр үлдээнэ, SQL*Plus-ийн `/` мөрийг хасна.
    """
    sql = sql.strip()
    if is_plsql_block(sql):
        return re.sub(r"\n\s*/\s*$", "", sql).rstrip()
    return sql.rstrip(";").rstrip()


def _code_mask(sql: str) -> str:
    """Comment, '...' доторхыг ижил урттай хоосон зай болгоно (байрлал хэвээр) — placeholder хайхад."""
    out, i, n = list(sql), 0, len(sql)
    while i < n:
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            j = n if j == -1 else j
        elif sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            j = n if j == -1 else j + 2
        elif sql[i] == "'":
            j = i + 1
            while j < n and not (sql[j] == "'" and not sql.startswith("''", j)):
                j += 2 if sql.startswith("''", j) else 1
            j = min(j + 1, n)
        else:
            i += 1
            continue
        for k in range(i, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


def shared_path(name: str, root: Path | None = None) -> Path:
    """{{shared.hr.active_employee}} → shared/hr/active_employee.sql"""
    return (root or SHARED_DIR).joinpath(*name.split(".")).with_suffix(".sql")


def shared_refs(sql: str) -> list[str]:
    """Кодонд иш татсан shared нэрс (comment, string доторхыг тооцохгүй)."""
    return _SHARED_RE.findall(_code_mask(sql))


def expand_shared(sql: str, root: Path | None = None, _stack: tuple = ()) -> str:
    """{{shared.name}}-ийг shared/name.sql-ийн SELECT-ээр (хаалтанд) солино. Дотроо дахин {{shared.x}} байж болно.

    Олон үзүүлэлтэд давхцдаг код (салбар↔sol холбоос, идэвхтэй ажилтан г.м.) нэг л газар бичигдэнэ.
    """
    root = root or SHARED_DIR
    out, last = [], 0
    for m in _SHARED_RE.finditer(_code_mask(sql)):       # comment, string доторхыг задлахгүй
        name = m.group(1)
        if name in _stack:
            raise ConfigError(f"shared тойрог: {' → '.join(_stack + (name,))}")
        path = shared_path(name, root)
        if not path.exists():
            raise ConfigError(f"{{{{shared.{name}}}}}: {path.relative_to(root.parent)} алга")
        body = clean_trailing(path.read_text(encoding="utf-8"))
        out += [sql[last:m.start()], "(\n", expand_shared(body, root, _stack + (name,)), "\n)"]
        last = m.end()
    return "".join(out) + sql[last:]
