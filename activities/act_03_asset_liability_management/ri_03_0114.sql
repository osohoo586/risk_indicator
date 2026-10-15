/*---
indicator_id: RI_03_0114
name_mn: "Нийт гадаад валютын нээлттэй позиц"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5- +30% < > -30%
  4- +26% < > -26%
  3- +22% < > -22%
  2- +18% < > -18%
  1- +14% < > -14%
source_system: "НУГ-АПУХ, СУГ, ДАГ-ЗАЧБХ"
required_info: "PR тайлан, СУГ-Метрик үзүүлэлт."
method: "Тухайн нэг гадаад валютын нээлттэй позиц/Өөрийн хөрөнгө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
