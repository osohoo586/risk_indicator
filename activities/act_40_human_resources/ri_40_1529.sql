/*---
indicator_id: RI_40_1529
name_mn: "Сахилгын арга хэмжээ авагдсан ажилтны тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Улиралд 10-аас бага
  2-Улиралд 11-13
  3-Улиралд 14-16
  4-Улиралд 17-20
  5-Улиралд 20-иос дээш
source_system: "ХНУГ"
required_info: "Сахилгын шийтгэл авагдсан тоо"
method: "Аудит орсноос хойш сахилгын шийтгэл авсан ажилтны улирлын дундаж тоо"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
