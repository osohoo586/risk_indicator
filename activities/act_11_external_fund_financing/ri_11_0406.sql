/*---
indicator_id: RI_11_0406
name_mn: "Гадны банкны зээлийн шугамын ашиглалт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-0-60%
  4-60-60.9%
  3-70-79.9%
  2-80-89.9%
  1-90-100%
source_system: "ХБСХ"
required_info: "Зээлийн шугамын ашиглалтын хувь"
method: "Шугам ашиглалтын хувийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
