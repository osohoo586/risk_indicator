/*---
indicator_id: RI_24_0895
name_mn: "Аккредитив цаг хугацаандаа хаагдсан байдалд хяналт тавьж буй байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хугацаандаа хаагдаагүй аккредитив байсан
  1-Бүх аккредитив хугацаандаа хаагдсан
source_system: "БТГ-АХ"
required_info: "Аккредитивийн тайлан"
method: "Хамрах хугацаанд идэвхитэй байсан аккредитивийн дуусах хугацааг хаасан хугацаатай харьцуулах"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
