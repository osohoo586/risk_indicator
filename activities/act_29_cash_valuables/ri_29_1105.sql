/*---
indicator_id: RI_29_1105
name_mn: "Нөөц кассын лимитийг барьж ажилласан эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "КҮЗХ"
required_info: "Лимитийн хэрэгжилт"
method: "Нөөц кассын лимитийн хэрэгжилтийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
