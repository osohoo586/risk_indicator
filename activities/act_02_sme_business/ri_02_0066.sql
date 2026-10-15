/*---
indicator_id: RI_02_0066
name_mn: "Хугацаа хэтэрсэн зээлийн харьцаа (PDL ratio) - БХГ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-5% түүнээс дээш
  4-0.05
  3-4-4.9%
  2-3-3.9%
  1-3%-аас бага
source_system: |
  BI тайлангийн систем
  ЗАЧБХ, ЭУГ-ЗЭУХ
required_info: "Зээлийн үлдэгдлийн мэдээлэл, ЗТУБХС"
method: "Анхаарал хандуулах зээл/Нийт зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
