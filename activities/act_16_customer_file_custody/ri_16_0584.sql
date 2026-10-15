/*---
indicator_id: RI_16_0584
name_mn: "Харилцагчийн хувийн хэргийг дэлгэрүүлэх, хянах, цахимжуулах хугацаа."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Ажлын 28 цаг, хугацааг хэмждэггүй
  4-Ажлын 27-28 цаг
  3-Ажлын 25-26 цаг
  2-Ажлын 24-25 цаг
  1-Ажлын 24 цагт багтсан
source_system: "ХБХХ"
required_info: "Хувийн хэрэг дэлгэрүүлсэн хугацаа"
method: "Хувийн хэрэг дэлгэрүүлсэн хугацаанд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
