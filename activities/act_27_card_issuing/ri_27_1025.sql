/*---
indicator_id: RI_27_1025
name_mn: "Луйврын гүйлгээ гарах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Луйврын гүйлгээ гарсан, банк алдагдал хүлээсэн.
  3-Луйврын гүйлгээ гарсан, банк алдагдал хүлээгээгүй.
  1-Луйврын гүйлгээ гараагүй
source_system: "ДБГ-КХ-КЭУА"
required_info: "Сэжигтэй гүйлгээ, chargeback-ийн тайлан"
method: "Луйврын гүйлгээ гарч банк алдагдал хүлээсэн эсэхийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
