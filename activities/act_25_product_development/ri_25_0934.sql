/*---
indicator_id: RI_25_0934
name_mn: "Бүтээгдэхүүн хөгжүүлэлтэд комплеансын дүгнэлт авахгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Бүх бүтээгдэхүүнд дүгнэлт авсан
  5-Дүгнэлт аваагүй тохиолдол гарсан
source_system: "БХХ-нарийн бичиг"
required_info: "Эрсдэлийн дүгнэлт"
method: "БХХ-оор хэлэлцүүлсэн шинэ болон одоогийн бүтээгдэхүүн сайжруулалтад комплеансын дүгнэлт аваагүй хэлэлцүүлсэн тохиолдол гарсан эсэхийг харгалзан үнэлнэ. 1 тохиолдол гарсан тохиолдолд 5 гэж үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
