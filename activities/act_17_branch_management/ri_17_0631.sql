/*---
indicator_id: RI_17_0631
name_mn: "Сегментийн бодлого тодорхойлсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Үгүй
  1-Тийм
source_system: "ИБГ-СУХ"
required_info: "Бодлого, журам"
method: "Бодлого тодорхойлогдож батлагдсан эсэхийг харгалзан дүгнэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
