/*---
indicator_id: RI_33_1257
name_mn: "Төлөвлөгдөөгүй худалдан авалт хийгдсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Төлөвлөгөөгүй худалдан авалт хийгдээгүй.
  2-Төлөвлөгөөгүй худалдан авалт 1 хийгдсэн
  3-Төлөвлөгөөгүй худалдан авалт 2-3 хийгдсэн
  4-Төлөвлөгөөгүй худалдан авалт 4-5 хийгдсэн
  5-Төлөвлөгөөгүй худалдан авалт 5-аас дээш хийгдсэн.
source_system: "СААХ"
required_info: "Худалдан авалтын мэдээ"
method: "Төлөвлөгдөөгүй худалдан авалт хийгдсэн эсэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
