/*---
indicator_id: RI_17_0637
name_mn: "Салбарын KPI хуваарилалт оновчтой эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Тийм
  0-Үгүй
source_system: "ДАГ"
required_info: "ДАГ-ын аудитын үр дүн"
method: "Аудит орсон нэгжүүд болон улирлын уулзалтаар төлөвлөгөө хуваарилалт үндэслэлгүй хийгдсэн тохиолдол гарсан эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
