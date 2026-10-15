/*---
indicator_id: RI_17_0638
name_mn: "Салбар, тооцооны төвийн ажилтнуудын орон тооны хангалт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ХНУГ"
required_info: "Банкны ажилтнуудын орон тооны хангалт"
method: "Ажиллаж буй ажилтны тоо/Нийт батлагдсан орон тоо"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
