/*---
indicator_id: RI_04_0150
name_mn: "Алтны тушаалтын хэмжээгээр банкны системд эзлэх хувь /Цэвэр дүнгээр/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-50%-аас бага
  4-0.5
  3-50-51.9%
  2-52-53.9%
  1-54%-аас дээш
source_system: "НУГ-АХ, СУГ метрик үзүүлэлт. Төв банкны ү.а-ны статистик МБ худалдан авсан алт"
required_info: "Алт тушаалтын мэдээ"
method: "МБ-ны нийт авсан алтны хэмжээ/Голомт банкнаас МБ-д тушаасан алтны хэмжээ."
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
