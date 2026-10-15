/*---
indicator_id: RI_28_1069
name_mn: "Монгол улсад POS-ийн төхөөрөмжид луйврын гүйлгээ гарсан эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Луйвар гарсан
  0-Луйвар гараагүй
source_system: "МБ мэдээлэл"
required_info: "Төлбөрийн системийн тайлан"
method: "Залилангийн гүйлгээний мэдээ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
