/*---
indicator_id: RI_25_0937
name_mn: "Үр ашгийн төлөвлөгөөний гүйцэтгэлийг хянадаг эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Тогтмол давтамжтай хянадаг
  3-Шаардлагатай үед хянадаг
  5-Хянадаггүй
source_system: "ИБГ-ИБХХ"
required_info: "Үр ашгийн төлөвлөгөөний гүйцэтгэл"
method: "Зах зээлд нэвтэрсэн бүтээгдэхүүний үр ашгийн хяналтыг хийдэг эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
