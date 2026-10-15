/*---
indicator_id: RI_03_0109
name_mn: "Бэлэн мөнгө (төгрөг) / Депозит (төгрөг)"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-1.3-аас бага
  2-1.3-1.39%
  3-1.4-1.49%
  4-1.5%-тай тэнцүү
  5-1.5%-аас их
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "Бэлэн мөнгө (төгрөг) / Депозит (төгрөг)"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
