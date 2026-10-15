/*---
indicator_id: RI_17_0628
name_mn: "Зээлийн төлөвлөгөө биелээгүй бизнес төв, салбар, ТТ-ийн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-46% ба түүнээс дээш биелээгүй
  4-31%-45% биелээгүй
  3-16%-30% биелээгүй
  2-1%-15% биелээгүй
  1-Төлөвлөгөө 100% биелсэн
source_system: "BI"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Төлөвлөгөө биелүүлсэн салбар/Нийт салбар"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
