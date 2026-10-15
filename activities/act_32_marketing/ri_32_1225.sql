/*---
indicator_id: RI_32_1225
name_mn: "Харилцагчийн сэтгэл ханамжийн индекс"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-90-100%
  2-80-89%
  3-70-79.9%
  4-65-69%
  5-0-64%, тооцдоггүй
source_system: "МХ"
required_info: "Судалгааны үр дүн"
method: "МХ-ийн харилцагчийн сэтгэл ханамжийн судалгааны үр дүнг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
