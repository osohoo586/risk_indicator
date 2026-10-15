/*---
indicator_id: RI_40_1530
name_mn: "Бэлгийн дарамт үзүүлсэн тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Тохиолдол гарсан
  0-Гараагүй
source_system: "Аудит хариуцсан захирал"
required_info: "Аудит хариуцсан захирал"
method: "Аудит хариуцсан захирлаас мэдээлэл авч үнэлнэ"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
