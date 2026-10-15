/*---
indicator_id: RI_24_0897
name_mn: "Үйлчилгээний шимтгэл хураамжийг бүрэн зөв авсан байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-3-с дээш тохиолдолд дутуу авсан
  4-Шимтгэл дутуу авсан 3
  3-Шимтгэл дутуу авсан 2
  2-Шимтгэл дутуу авсан 1
  1-Бүрэн авсан
source_system: "БТГ-АХ"
required_info: "Нээгдсэн аккредитивийн тоог шимтгэлтэй харьцуулах"
method: "Дутуу авсан шимтгэл байгаа эсэхийг баталгаажуулах"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
