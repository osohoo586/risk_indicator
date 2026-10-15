/*---
indicator_id: RI_23_0857
name_mn: "Банкны төв байрнуудын биет аюулгүй байдлын стандартын хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-94-с доош хувь, шалгаагүй
  4-94-95%
  3-96-97%
  2-98-99%
  1-100 хувь хэрэгжүүлсэн
source_system: "АБХ"
required_info: "Биет аюулгүй байдлын стандарт хэрэгжилтийн мэдээ"
method: |
  Хагас жил стандарт хэрэгжилт шалгадаг. Стандарт хэрэгжилтийн шалгалтын үнэлгээ
  - Үнэмлэхгүй нэвтэрсэн тохиолдол гарсан эсэх
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
