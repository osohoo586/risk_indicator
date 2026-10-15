/*---
indicator_id: RI_02_0095
name_mn: "Бодлого, стратегид тусгасан зорилтын хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 5                       # үйл ажиллагаа доторх жин (%)
score_type: "score5"
scale_text: |
  1-Бага
  3-Дунд
  5-Өндөр
source_system: "Нэгжийн тайлан мэдээлэл"
required_info: "Хамрах хугацааны тайлан мэдээлэл"
method: "Үйл ажиллагаатай холбоотой хийгдсэн ажлын Стратегийн ач холбогдлын зэргээр үнэлнэ"
period_text: "Хамрах улирал"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
