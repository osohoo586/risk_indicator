/*---
indicator_id: RI_36_1371
name_mn: "ЗТУБАХС хүрэлцээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-70% ба түүнээс доош
  4-71%-73%
  3-74%-77%
  2-77%-80%
  1-80% ба түүнээс дээш
source_system: |
  BI тайлангийн систем
  ЗАЧБХ, ЭУГ-ЗЭУХ
required_info: "Зээлийн үлдэгдлийн мэдээлэл, ЗТУБХС"
method: "Зээлийн эрсдэлийн сан/Чанаргүй зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
