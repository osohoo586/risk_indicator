/*---
indicator_id: RI_27_1026
name_mn: "Charge back -н үйл ажиллагаанд банк ялагдах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Банк ялсан, банк болон харилцагч алдагдал хүлээгээгүй.
  3-Банк ялагдсан ч, алдагдал хүлээгээгүй. /Харилцагчийн буруу/
  5-Банк алдагдал хүлээсэн
source_system: "ДБГ-КХ-КЭУА"
required_info: "Сэжигтэй гүйлгээ, chargeback-ийн тайлан"
method: "Банк ялагдсан тохиолдол гарсан эсэхийг харгалзаж үнэлэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
