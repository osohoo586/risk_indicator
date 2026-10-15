/*---
indicator_id: RI_29_1097
name_mn: "Нөөц касс болон тоолох тасгийн стандарт зөрчсөн тохиолдол илэрсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-4 шаардлага хангаагүй
  4-3 шаардлага хангаагүй
  3-2 шаардлага хангаагүй
  2-1 шаардлага хангаагүй
  1-Бүх шаардлагыг хангасан
source_system: "КҮЗХ"
required_info: "Стандарт хэрэгжилтийн шалгалтын үр дүн"
method: "Нөөц кассын 8 стандарт, Тоолох тасгийн 6 стандартын хэрэгжилт"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
