/*---
indicator_id: RI_09_0345
name_mn: "Санхүүгийн үр дүнтэй холбоотой мэдээллийг зөрүүтэй тайлагнасан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрүүтэй тайлагнасан тохиолдол гарсан.
  1-Зөрүүтэй тайлагнасан тохиолдол гараагүй.
source_system: |
  СУГ-ББХХ,
  ДАГ-ЗАЧБХ
required_info: "Санхүүгийн үр дүн зөрсөн тохиолдол"
method: "Аудитын хороо болон Актив пассивын хорооны мэдээллийн нийцлээр баталгаажуулах"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
