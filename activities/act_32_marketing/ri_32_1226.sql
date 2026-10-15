/*---
indicator_id: RI_32_1226
name_mn: "Судалгааны төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Судалгааны гүйцэтгэл 90-с дээш хувь
  3-Судалгааны гүйцэтгэл 60-90 хувь
  5-Судалгааны гүйцэтгэл 59-с доош хувь
source_system: "МХ"
required_info: "Action plan-ийн хэрэгжилт"
method: "Төлөвлөсөн судалгааны гүйцэтгэл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
