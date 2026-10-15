/*---
indicator_id: RI_27_1030
name_mn: "Картын пластикийн чипний хугацаа дуусч ашиглагдах боломжгүй болсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Гарсан.
  0-Гараагүй
source_system: "ДБГ-КХ"
required_info: "ДБГ-КХ-ээс мэдээлэл авах"
method: "Хэвлэсэн картын чипний хугацаа дуусч ашиглах боломжгүй тохиолдол гарсан  эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
