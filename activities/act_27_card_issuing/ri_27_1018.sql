/*---
indicator_id: RI_27_1018
name_mn: "Картын шимтгэлийн орлогын төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "КХ, СУГ-Метрик"
required_info: "Төлөвлөгөөний гүйцэтгэл"
method: "Картын шимтгэлийн орлого/Төлөвлөгөө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
