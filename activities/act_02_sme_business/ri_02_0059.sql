/*---
indicator_id: RI_02_0059
name_mn: "Дижитал идэвхтэй харилцагчийн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
source_system: "BI тайлангийн систем"
required_info: "SME идэвхтэй харилцагчийн тоо"
method: "Харилцагчийн тоон төлөвлөгөөний биелэлт"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
