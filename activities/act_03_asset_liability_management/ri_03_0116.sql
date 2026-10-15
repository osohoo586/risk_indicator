/*---
indicator_id: RI_03_0116
name_mn: "Санхүүгийн үүсмэл хэрэгсэлтэй холбоотой тайлан мэдээг алдаатай гаргах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-МБанк руу өгч байгаа тайлан мэдээг алдаатай гаргах
  3-Дотоод тайлан мэдээг алдаатай гаргах
  1-Зөрчил гараагүй
source_system: "ДАГ-ЗАЧБХ"
required_info: "PR тайлан"
method: "Санхүүгийн үүсмэл хэрэгсэлтэй холбоотой тайлан мэдээг алдаатай гаргасан тохиолдол байгаа эсэхийг ДАГ-ЗАЧБХ-ээс авч дүгнэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
