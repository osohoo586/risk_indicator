/*---
indicator_id: RI_36_1375
name_mn: "Зээлийн scoring-ийн загварын тайлбарлах чадвар хангалтгүй байх. /GINI тооцоолол/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-70-с дээш хувь
  2-60-70-с дээш хувь
  3-50-59-с  хувь
  4-41-49-с  хувь
  5-40-с бага хувь, backtest хийж баталгаажуулаагүй байх.
source_system: "ЗГ-ЗБХ"
required_info: "Scoring-ийн тайлбарлах чадвар"
method: "Scoring-ийн загварын тайлбарлах чадварыг илэрхийлсэн backtest-ийн үр дүнг ЗБХ-ээс авна. GINI коефциентоор үнэлнэ"
period_text: |
  Хамгийн сүүлд хийгдсэн backtest
  Сүүлийн жилд
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
