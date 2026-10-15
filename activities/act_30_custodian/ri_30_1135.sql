/*---
indicator_id: RI_30_1135
name_mn: "Физик аюулгүй байдлыг хангаж ажиллаж буй байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Аюулгүй байдал хангалтгүй
  3-Аюулгүй байдал бүрэн хангагдаагүй
  1-Аюулгүй байдал бүрэн хангагдсан
source_system: "Кастодиан банк"
required_info: "Физик аюулгүй байдлын дүгнэлт"
method: "КБ-ээс ирсэн мэдээлэлд үндэслэнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
