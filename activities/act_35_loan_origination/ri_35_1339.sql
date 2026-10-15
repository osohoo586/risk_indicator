/*---
indicator_id: RI_35_1339
name_mn: "Зээлийн хороодын ирц"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ЗГ"
required_info: "Зээлийн хорооны ирц"
method: "Аудит орсноос хойш хугацааны ирцийг дунджийг тодорхойлж үнэлнэ."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
