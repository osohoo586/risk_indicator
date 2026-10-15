/*---
indicator_id: RI_28_1058
name_mn: "Киоскын тоон төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
  0-Төлөвлөгөө өгөгдөөгүй /Үнэлэхгүй/
source_system: "ДБГ-ЦХАХ, СУГ-Метрик"
required_info: "Төлөвлөгөөний гүйцэтгэл"
method: "Киоск тоо/Төлөвлөгөө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
