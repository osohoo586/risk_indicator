/*---
indicator_id: RI_16_0586
name_mn: "Хувийн хэрэгт гарсан зөрчлийн засагдсан хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-80% засагдсан
  4-85% засагдсан
  3-90% засагдсан
  2-95% засагдсан
  1-Бүх зөрчил засагдсан
source_system: "ХБХХ"
required_info: "Хувийн хэргийн зөрчлийн мэдээлэл"
method: "Илэрсэн зөрчлийн засагдсан хувийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
