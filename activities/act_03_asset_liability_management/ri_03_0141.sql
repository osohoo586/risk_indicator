/*---
indicator_id: RI_03_0141
name_mn: "Актив пассивын бодлого шинэчлэгдсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score4"
scale_text: |
  5-Сүүлийн 1 жилд шинэчлэгдээгүй.
  1-Сүүлийн 1 жил шинэчилсэн.
source_system: "НУГ-АПУХ"
required_info: "АП-ын бодлого. /Шинэчлэгдсэн огноо/"
method: "Актив пассивын бодлого шинэчлэгдсэн огноог харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
