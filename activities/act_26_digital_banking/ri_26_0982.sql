/*---
indicator_id: RI_26_0982
name_mn: "Дижитал сувгаар луйврын гүйлгээ гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Луйврын гүйлгээ гарсан
  0-Луйврын гүйлгээ гараагүй /Үнэлэхгүй/
source_system: "ДАГ, ЭУГ, КХ"
required_info: "ДАГ, ЭУГ, КХ-с мэдээллүүд авна. Гомдолд үндэслэн тооцно."
method: "Гомдолд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
