/*---
indicator_id: RI_03_0099
name_mn: "АПХорооны ирц"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-85%-с доош
  4-85%-85.9%
  3-86-86.9%
  2-87-89.9%
  1-90%-с дээш
source_system: "НУГ-АПУХ"
required_info: "АПХорооны ирцийн мэдээлэл"
method: |
  АПХ-ны ирцийн мэдээллийг АПХорооны нарийн бичгээс авна.
  (Хороонд ирсэн гишүүд*хуралдсан тоо)/(Хорооны нийт гишүүд*Хуралдсан тоо)
period_text: "Аудит орсноос хойш улирлын дундаж."
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
