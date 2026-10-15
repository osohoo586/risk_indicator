/*---
indicator_id: RI_40_1522
name_mn: "Нэг ажилтанд ногдох орлогын хэмжээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Өмнөх жилтэй харьцуулахад буурсан
  3-Өмнөх жилтэй тэнцүү
  1-Өмнөх жилтэй харьцуулахад өссөн
source_system: "ХНУГ, СУГ-метрик"
required_info: "Үйл ажиллагааны орлого, Ажилтны тоо"
method: "Үйл ажиллагааны орлого/Нийт ажилтны тоо(ажиллаж байгаа)"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
