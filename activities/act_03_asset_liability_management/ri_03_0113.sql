/*---
indicator_id: RI_03_0113
name_mn: "Нэг гадаад валютын нээлттэй позиц"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5- +15% < > -15%
  4- +13% < > -13%
  3- +11% < > -11%
  2- +9% < > -9%
  1- +7% < > -7%
source_system: "НУГ-АПУХ, СУГ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "Тухайн нэг гадаад валютын нээлттэй позиц/Өөрийн хөрөнгө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
