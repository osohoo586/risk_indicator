/*---
indicator_id: RI_10_0373
name_mn: "Шинээр харилцагчаар татсан санхүүгийн байгууллагын тоо."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Шинээр харилцаа тогтоогоогүй
  4-1 байгууллага
  3-2 байгууллага
  2-3 байгууллага
  1-3-с дээш байгууллага
source_system: "СБХ"
required_info: "Шинээр харилцаа тогтоосон санхүүгийн байгууллагын мэдээ"
method: "Нэгжээс авсан мэдээллийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
