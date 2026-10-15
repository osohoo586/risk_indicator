/*---
indicator_id: RI_34_1294
name_mn: "Төслийн удирдагч, администратор солигдсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Удирдагч, эсвэл администратор солигдсон
  1-Удирдагч, эсвэл администратор солигдоогүй
source_system: "ДШГ-ТУХ"
required_info: "Төслийн удирдагчийн мэдээлэл"
method: "Солигдсон эсэхийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
