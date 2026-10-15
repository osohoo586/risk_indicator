/*---
indicator_id: RI_09_0342
name_mn: "Бүртгэлийн үйл ажиллагаанд хийсэн мониторингийн үр дүн тайлагнагдахгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Мониторингийн үр дүнг бүрэн тайлагнасан
  3-Мониторингийн зарим үр дүнг тайлагнасан
  5-Мониторингийн үр дүнг тайлагнаагүй
source_system: "СБМХ"
required_info: "Мониторингийн үр дүнгийн тайлан"
method: "Бүртгэлийн мониторингийн үр дүнг тайлагнасан эсэхийг харгалзан үнэлнэ"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
