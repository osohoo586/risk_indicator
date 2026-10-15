/*---
indicator_id: RI_15_0549
name_mn: "Хувийн банкны салбаруудын дотоод ашгийн төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "Oracle BI тайлангийн систем"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Хувийн банкны салбаруудын төлөвлөгөөний гүйцэтгэлээр үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
