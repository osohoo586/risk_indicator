/*---
indicator_id: RI_40_1523
name_mn: "Нэг ажилтанд ногдох үйл ажиллагааны зардллын хэмжээ.\n/цалин, урамшууллын зардлыг оруулахгүй/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Өмнөх жилтэй харьцуулахад өссөн
  3-Өмнөх жилтэй тэнцүү
  1-Өмнөх жилтэй харьцуулахад буурсан
source_system: "ХНУГ"
required_info: "Үйл ажиллагааны зардал, Нийт ажилтны тоо"
method: "Үйл ажиллагааны зардлаас - ЦЗ / Нийт ажилтнуудын тоо"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
