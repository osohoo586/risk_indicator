/*---
indicator_id: RI_37_1413
name_mn: "ӨБҮХХ/Нийт зээл"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-10%-аас их
  4-5-9.9%
  3-4%-5%
  2-3%-3.9%
  1-3%-аас бага
source_system: "ДАГ-ЗАЧБХ, СУГ-метрик"
required_info: "Зээлийн тайлан, ӨБҮХХ-ийн хэмжээ"
method: "ӨБҮХХ/Нийт зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
