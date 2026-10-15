/*---
indicator_id: RI_39_1490
name_mn: "Дуудлага хүлээлгийн хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-0-25 секунд
  2-25-39 секунд
  3-30-34 секунд
  4-35-39 секунд
  5-40 секундээс дээш
source_system: "ХҮХ, СУГ"
required_info: "Дуудлага хүлээлгийн хугацаа"
method: "Дуудлага хүлээлгийн хугацааг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
