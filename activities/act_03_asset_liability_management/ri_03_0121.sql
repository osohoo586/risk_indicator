/*---
indicator_id: RI_03_0121
name_mn: "Стандарт хугацаанд гаргасан тайлангийн хувь"
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
source_system: "АПУХ"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Стандарт хугацаанд илгээсэн тайлан илгээсэн эсэх гүйцэтгэлээр үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
