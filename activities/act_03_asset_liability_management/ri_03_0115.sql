/*---
indicator_id: RI_03_0115
name_mn: "Хөрөнгө оруулалтын үнэт цаас/Нийт актив"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-3.4%-с дээш
  4-3.3%-3.39%
  3-3.2%-3.29%
  2-3.1%-3.19%
  1-3.1%-с доош
  0-Үнэлэхгүй
source_system: "ДАГ-ЗАЧБХ, НУГ-АПУХ"
required_info: "PR тайлан, АПУХ-ийн мэдээлэл"
method: "Хөрөнгө оруулалтын үнэт цаас/Нийт актив"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
