/*---
indicator_id: RI_39_1485
name_mn: "Дуудлага хүлээн авсан байдал/алдсан дуудлагын тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-80%-с доош
  4-80%-84.9%
  3-85%-89.9%
  2-90%-92.9%
  1-93% ба түүнээс дээш
source_system: "ХҮХ"
required_info: "Дуудлага хүлээн авалтын мэдээ"
method: |
  Амжилттай дуудлагын тоо / Нийт дуудлагын тоо
  Анхны дуудлагаар хүлээн авах.
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
