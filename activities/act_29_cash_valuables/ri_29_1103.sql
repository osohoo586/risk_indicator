/*---
indicator_id: RI_29_1103
name_mn: "Шимтгэлийн орлого - Цүнхээр мөнгө хураах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
source_system: "КҮЗХ, СУГ-Метрик"
required_info: "Орлогын төлөвлөгөөний биелэлт"
method: "Шимтгэлийн орлогын гүйцэтгэл/Шимтгэлийн орлогын төлөвлөгөө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
