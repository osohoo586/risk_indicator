"""Нэг үйл ажиллагааны (BRANCHID) тайлан — локал HTML файл (интернэтэд гарахгүй).

    python ri.py report --env dev -a 998 -d 2026-09-30        → output/report_998_20260930.html

Бүтэц:  нийт оноо → master-ийн Score бүлгээр (score1…score6) үзүүлэлтүүд → үзүүлэлт дээр дарахад SOL задаргаа.
ri_result-д мөргүй үзүүлэлт (TODO, бөглөөгүй manual) ч жагсаалтад харагдана.
"""
import datetime as dt
import html
from collections import defaultdict
from pathlib import Path

from . import store
from .config import OUTPUT_DIR, EnvConfig, load_scoring
from .db import connect
from .metadata import Catalog, Indicator

MODE_LABEL = {"sql": "SQL", "shared": "Нийтлэг SQL", "manual": "Гараар"}


def _e(v) -> str:
    return html.escape("" if v is None else str(v))


def _fmt_value(ind: Indicator, value, text) -> str:
    if text not in (None, ""):
        return _e(text)
    if value is None:
        return "—"
    v = float(value)
    if ind.scale and ind.scale.get("unit") == "percent" and ind.value_unit == "ratio":
        return f"{v * 100:,.1f}%"
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v:,.4g}"


def _score_cls(score) -> str:
    if score is None:
        return "s-none"
    return f"s{int(round(float(score)))}"


def _level_cls(level: str) -> str:
    return {"Өндөр": "lv-high", "Дунд": "lv-mid", "Бага": "lv-low"}.get(level or "", "lv-none")


def _query(cfg: EnvConfig, conn, branch_id: str, d: dt.date):
    db, t = f"`{cfg.result_db}`", store.RESULT_TABLE
    p = {"b": str(branch_id), "d": d}
    cols, act = conn.query(
        f"SELECT value, level, n_scored, n_indicators, weight_coverage, loaded_at FROM {db}.{t} "
        f"WHERE branch_id = {{b:String}} AND report_date = {{d:Date}} AND row_type = 'ACTIVITY'", p)
    _, ind = conn.query(
        f"SELECT indicator_id, source_kind, value, value_text, score, score_label, weight, numerator, denominator, "
        f"comment, entered_by, loaded_at FROM {db}.{t} WHERE branch_id = {{b:String}} AND report_date = {{d:Date}} "
        f"AND row_type = 'INDICATOR' AND entity_level = 'ACTIVITY'", p)
    _, sol = conn.query(
        f"SELECT indicator_id, entity_level, entity_id, entity_name, numerator, denominator, value FROM {db}.{t} "
        f"WHERE branch_id = {{b:String}} AND report_date = {{d:Date}} AND row_type = 'INDICATOR' "
        f"AND entity_level != 'ACTIVITY' ORDER BY indicator_id, value", p)
    _, hist = conn.query(
        f"SELECT report_date, value, level FROM {db}.{t} WHERE branch_id = {{b:String}} AND row_type = 'ACTIVITY' "
        f"AND report_date <= {{d:Date}} ORDER BY report_date DESC LIMIT 6", p)
    return (act[0] if act else None), ind, sol, hist


def build(cfg: EnvConfig, cat: Catalog, activity_key: str, d: dt.date, path: Path | None = None) -> Path:
    act = cat.resolve_activity(activity_key)
    if not act.branch_id:
        raise ValueError(f"{act.activity_id}-д BRANCHID алга")
    with connect(cfg, cfg.result_connection) as conn:
        act_row, ind_rows, sol_rows, hist = _query(cfg, conn, act.branch_id, d)
    res = {r[0]: r for r in ind_rows}
    sols = defaultdict(list)
    for r in sol_rows:
        sols[r[0]].append(r)

    groups = load_scoring(cfg)["groups"]
    inds = [i for i in cat.by_activity(act.activity_id) if i.enabled and not i.example]
    by_group = defaultdict(list)
    for i in inds:
        by_group[(i.score_type or "бусад").lower()].append(i)

    def g_stats(items):
        tw = sum(i.weight or 0 for i in items)
        sc = [(float(res[i.indicator_id][4]), i.weight or 0) for i in items
              if i.indicator_id in res and res[i.indicator_id][4] is not None and i.weight]
        sw = sum(w for _, w in sc)
        return tw, (sum(s * w for s, w in sc) / sw if sw else None), len(sc)

    score = act_row[0] if act_row else None
    level = act_row[1] if act_row else ""
    cov = act_row[4] if act_row else None
    n_scored = act_row[2] if act_row else 0

    out = []
    w = out.append
    w(f"""<!doctype html><html lang="mn"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(act.name_mn)} — {d}</title>
<style>
:root{{--bg:#f7f7f5;--card:#fff;--fg:#1d1d1b;--mut:#6b6b66;--line:#e4e4df;--acc:#2d5bd7;
--s1:#2e9d5b;--s2:#8cbf3f;--s3:#e0b72b;--s4:#e5803a;--s5:#d1453b;}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--card:#1f1f1d;--fg:#ececea;--mut:#9a9a94;--line:#33332f;--acc:#7da0ff;}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:20px 16px 60px}}
h1{{font-size:22px;margin:0 0 4px}} .mut{{color:var(--mut)}}
.top{{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0 22px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:150px}}
.kpi b{{display:block;font-size:24px}} .kpi span{{color:var(--mut);font-size:12px}}
.lv-high b{{color:var(--s5)}} .lv-mid b{{color:var(--s3)}} .lv-low b{{color:var(--s1)}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:0 0 16px;overflow:hidden}}
section>header{{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line)}}
section>header h2{{font-size:15px;margin:0}}
.row{{border-bottom:1px solid var(--line)}} .row:last-child{{border-bottom:0}}
summary{{list-style:none;cursor:pointer;display:grid;grid-template-columns:96px 1fr 90px 110px 64px 1fr;gap:10px;align-items:center;padding:9px 16px}}
summary::-webkit-details-marker{{display:none}} details[open] summary{{background:color-mix(in srgb,var(--acc) 7%,transparent)}}
.id{{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--mut)}}
.tag{{font-size:11px;padding:1px 6px;border-radius:9px;border:1px solid var(--line);color:var(--mut);white-space:nowrap}}
.sc{{display:inline-block;min-width:34px;text-align:center;font-weight:700;border-radius:6px;padding:2px 6px;color:#fff}}
.s1{{background:var(--s1)}} .s2{{background:var(--s2)}} .s3{{background:var(--s3)}} .s4{{background:var(--s4)}} .s5{{background:var(--s5)}}
.s-none{{background:transparent;color:var(--mut);border:1px dashed var(--line)}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}
.det{{padding:6px 16px 14px 122px;font-size:13px}} .det table{{border-collapse:collapse;width:100%;max-width:720px}}
.det th,.det td{{padding:4px 8px;border-bottom:1px solid var(--line);text-align:left}} .det th{{color:var(--mut);font-weight:500}}
.scale{{white-space:pre-line;color:var(--mut);font-size:12px;margin:6px 0}}
@media (max-width:760px){{summary{{grid-template-columns:1fr auto;}} summary .hide-m{{display:none}} .det{{padding-left:16px}}}}
</style></head><body><main>
<div class="mut">BRANCHID {_e(act.branch_id)} · {_e(act.activity_id)} · тайлант огноо {d} · {_e(cfg.env)}</div>
<h1>{_e(act.name_mn)}</h1>
<div class="top">
 <div class="kpi {_level_cls(level)}"><span>Нийт оноо</span><b>{'—' if score is None else f'{float(score):.2f}'}</b></div>
 <div class="kpi {_level_cls(level)}"><span>Эрсдэлийн түвшин</span><b>{_e(level or '—')}</b></div>
 <div class="kpi"><span>Оноотой үзүүлэлт</span><b>{n_scored or 0} / {len(inds)}</b></div>
 <div class="kpi"><span>Жингийн хамралт</span><b>{'—' if cov is None else f'{float(cov) * 100:.0f}%'}</b></div>
</div>""")
    if hist and len(hist) > 1:
        w('<p class="mut">Өмнөх үеүүд: ' + " · ".join(
            f"{h[0]}: {'—' if h[1] is None else f'{float(h[1]):.2f}'} {_e(h[2])}" for h in reversed(hist)) + "</p>")

    for gkey in sorted(by_group, key=lambda k: (k not in groups, k)):
        items = by_group[gkey]
        tw, gavg, gn = g_stats(items)
        w(f'<section><header><h2>{_e(gkey.capitalize())} · {_e(groups.get(gkey, ""))}</h2>'
          f'<span class="mut">жин {tw:g}% · оноотой {gn}/{len(items)} · дундаж '
          f'{"—" if gavg is None else f"{gavg:.2f}"}</span></header>')
        for i in items:
            r = res.get(i.indicator_id)
            sc = None if not r else r[4]
            if r:
                state = MODE_LABEL.get(i.mode, i.mode)
            elif i.mode == "manual":
                state = "Бөглөөгүй"
            elif i.status == "TODO":
                state = "SQL бичигдээгүй"
            else:
                state = "Ажиллаагүй"
            w('<details class="row"><summary>'
              f'<span class="id">{_e(i.indicator_no)}</span>'
              f'<span>{_e(i.name_mn)} <span class="id">{_e(i.indicator_id)}</span></span>'
              f'<span class="num hide-m">{_fmt_value(i, r[2] if r else None, r[3] if r else None)}</span>'
              f'<span class="hide-m"><span class="tag">{_e(state)}</span></span>'
              f'<span><span class="sc {_score_cls(sc)}">{"—" if sc is None else f"{float(sc):g}"}</span></span>'
              f'<span class="mut hide-m">жин {i.weight or 0:g}% · {_e((r[5] if r else "") or "")}</span>'
              '</summary><div class="det">')
            if i.scale_text:
                w(f'<div class="scale">Шатлал:\n{_e(i.scale_text.strip())}</div>')
            if r and (r[7] is not None or r[8] is not None):
                w(f'<div>Хүртвэр: <b>{_fmt_num(r[7])}</b> · Хуваарь: <b>{_fmt_num(r[8])}</b></div>')
            if r and (r[9] or r[10]):
                w(f'<div class="mut">{_e(r[9] or "")} {("— " + _e(r[10])) if r[10] else ""}</div>')
            detail = sols.get(i.indicator_id, [])
            if detail:
                w('<table><tr><th>SOL</th><th>Нэр</th><th class="num">Хүртвэр</th><th class="num">Хуваарь</th>'
                  '<th class="num">Утга</th></tr>')
                for _, lvl, eid, ename, num, den, val in detail:
                    w(f'<tr><td class="id">{_e(eid)}</td><td>{_e(ename)}</td><td class="num">{_fmt_num(num)}</td>'
                      f'<td class="num">{_fmt_num(den)}</td><td class="num">{_fmt_value(i, val, None)}</td></tr>')
                w('</table>')
            elif not r:
                src = i.master.get("source_system") or ""
                w(f'<div class="mut">Мэдээлэл алга. {("Эх сурвалж: " + _e(src)) if src else ""}</div>')
            w('</div></details>')
        w('</section>')
    w(f'<p class="mut">Үүсгэсэн: {dt.datetime.now():%Y-%m-%d %H:%M} · {_e(cfg.result_db)}.{store.RESULT_TABLE}</p>'
      '</main></body></html>')

    path = path or OUTPUT_DIR / f"report_{act.branch_id}_{d:%Y%m%d}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out), encoding="utf-8")
    return path


def _fmt_num(v) -> str:
    if v is None:
        return "—"
    v = float(v)
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.4g}"
