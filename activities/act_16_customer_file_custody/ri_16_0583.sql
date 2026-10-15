/*---
indicator_id: RI_16_0583
name_mn: "Өдрийн баримтыг хянаж баталгаажуулсан хугацаа."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-11-аас дээш цаг, хугацааг хэмждэггүй
  4-10-11 цаг
  3-9-10 цаг
  2-8-9 цаг
  1-8-аас доош цаг
source_system: "ХБХХ"
required_info: "Баримт хянасан хугацаа"
method: "Стандарт хугацаа хангасан эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
