/*---
indicator_id: RI_22_0815
name_mn: "Хөрөнгө оруулагчдад хүргэх санхүүгийн тайлан, үр дүнг хугацаанд нь хүргүүлж ажилладаг эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Хоцроосон тохиолдол гараагүй.
  5-Хоцроосон тохиолдол гарсан.
source_system: "ХОХХ"
required_info: "Хамрах хугацаанд хөрөнгө оруулагч нарт хүргүүлсэн мэдээлэл"
method: "Хамрах хугацаанд хөрөнгө оруулагч нарт илгээсэн тайлан, мэдээлэлд үндэслэн дүгнэнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
