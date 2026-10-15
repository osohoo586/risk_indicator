/*---
indicator_id: RI_16_0596
name_mn: "Ложистикийн тээврийн хэрэгслийн аюулгүй байдлын стандартын хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Бүх машины стандартыг шалгаагүй, хэрэгжилт 85%-аас доош
  4-Хэрэгжилт 85-89%
  3-Хэрэгжилт 90-94%
  2-Хэрэгжилт 95-99%
  1-Хэрэгжилт 100%
source_system: "ХБГ-АЛА"
required_info: "Тээврийн хэрэгслийн хяналтын үр дүн"
method: "Аюулгүй байдлын стандарт шаардлага хангаагүй автомашин байгаа эсэхийг харгалзаж үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
