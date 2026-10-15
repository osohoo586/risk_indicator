/*---
indicator_id: RI_36_1369
name_mn: "Бүтэц өөрчилсөн зээл"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-10% ба түүнээс дээш
  4-9%-9.9%
  3-5%-8.9%
  2-1%-4%
  1-0
source_system: |
  ЭУГ - ЗЭУХ
  ДАГ-ЗАЧБХ
required_info: "ЭУГ-Breakdown тайлан"
method: "Бүтэц өөрчилсөн/Нийт зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
