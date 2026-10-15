/*---
indicator_id: RI_37_1419
name_mn: "Зарцуулалтын болон явцын хяналт хийсэн байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-0-79%
  4-80%-84%
  3-85%-89%
  2-90%-94%
  1-95%-аас дээш
source_system: "ЗГ-МХ"
required_info: "ЗГ-Мониторингийн хэлтсийн хяналтын үр дүн"
method: "МХ-ийн үр дүнд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш улирал бүрийн дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
