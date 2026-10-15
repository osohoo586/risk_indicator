/*---
indicator_id: RI_19_0715
name_mn: "Хураамжийн орлого"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  90% ба түүнээс доош-Тийм
  91%-93%-
  94%-96%-
  97%-99%-
  100% ба түүнээс дээш-
source_system: "BI"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Нийт шимтгэлийн хураамжийн орлогын төлөвлөгөө, гүйцэтгэл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
