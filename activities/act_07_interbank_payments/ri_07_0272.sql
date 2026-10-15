/*---
indicator_id: RI_07_0272
name_mn: "Системийн тасралт өндөр байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  Сүүлийн 1 жил-5
  -3
  -1
source_system: "ДАГ-МТАХ"
required_info: "Системийн тасралтын мэдээлэл"
method: "Системийн тасралтын эрсдэлийн лимит болон, Монгол банкны шалгуурыг зөрчсөн тохиолдол гарсан эсэхийг харгалзна."
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
