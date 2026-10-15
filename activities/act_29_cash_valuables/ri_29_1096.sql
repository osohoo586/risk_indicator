/*---
indicator_id: RI_29_1096
name_mn: "Салбар, ТТ-үүдийн кассын лимит хэрэгжихгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Хамрах хугацаанд кассын лимит хэтрээгүй.
  3-Хамрах хугацааны 0.1-2 хувьд кассын лимит хэтэрсэн
  5-Хамрах хугацааны 2 дээш хувьд кассын лимит хэтэрсэн
source_system: "БТГ-КҮЗХ"
required_info: "Кассын лимитийн хэрэгжилт"
method: |
  Кассын лимит хэтэрсэн тохиолдол/Нийт тохиолдол
  Нийт тохиолдол=салбар нэгжийн тоо*хоног*валютын тоо
period_text: "Сүүлийн улиралд"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
