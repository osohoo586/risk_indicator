/*---
indicator_id: RI_16_0587
name_mn: "Хувийн хэргээс илрүүлсэн зөрчлийн тоо бодит зөрчлөөс бага байх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Давхар хяналтаар зөрчил илэрсэн
  1-Давхар хяналтаар зөрчил илрээгүй
source_system: "ХБХХ"
required_info: "Ажилтны зөрчлийн тоо"
method: "Хувийн хэргийн зөрчлийг бүртгэсэн ажилтанд давхар хяналт хийхэд зөрчлийг дутуу илрүүлсэн эсэхийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
