/*---
indicator_id: RI_39_1487
name_mn: "Харилцагчийн асуудал, гомдол шийдвэрлэлт -анхны хандалтаар шийдвэрлэсэн хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-20 минутаас дээш
  4-14-20 минут
  3-12-14 минут
  2-10-12 минут
  1-0-10 минут
source_system: "ГУХ"
required_info: "Гомдол шийдвэрлэсэн хугацаа"
method: "Гомдол шийдвэрлэсэн хугацаанд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
