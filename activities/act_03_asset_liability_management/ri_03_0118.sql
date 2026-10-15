/*---
indicator_id: RI_03_0118
name_mn: "Нийт харилцагчын тоо  -Wealth Management"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-15 өдөрт
  2-16 өдөрт
  3-17 өдөрт
  4-18 өдөрт
  5-19-с дээш өдөрт. Судалгааны хурдыг хэмждэггүй.
source_system: "BI"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Тухайн тайлант хугацаанд  гэрээ байгуулсан харилцагчдын багцын тоо буюу Client code"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
