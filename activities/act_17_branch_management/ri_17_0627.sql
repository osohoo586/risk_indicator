/*---
indicator_id: RI_17_0627
name_mn: "Бизнес төв, салбар, ТТ -ийн дотоод ашгийн төлөвлөгөөний биелэлт"
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
source_system: "BI"
required_info: "Орлого үр дүнгийн тайлан"
method: "Төлөвлөгөөний гүйцэтгэлийг харгалзан үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
