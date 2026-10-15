/*---
indicator_id: RI_30_1140
name_mn: "Кастодианы харилцагчийн тоогоор банкны системд эзлэх хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-40-41.9%
  4-42-43.9%
  3-44-45.9%
  2-46-49.9%
  1-50%-аас дээш
source_system: "Кастодиан банк"
required_info: "Зах зээлд эзлэх хувь"
method: "Зах зээлд эзлэх хувийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
