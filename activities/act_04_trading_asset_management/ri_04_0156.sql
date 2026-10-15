/*---
indicator_id: RI_04_0156
name_mn: "Хувьцааны сонголт хийх судалгаа (Wealth management)"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Судалгаа хийж гүйцэтгээгүй.
  1-Судалгааг гүйцэтгэж, газрын захирлаар батлуулсан.
source_system: "НУГ-АХ"
required_info: "Судалгаа, тайлан, мэдээ гаргалтын тоо"
method: "Тайлант хугацааны төлөвлөгөөний биелэлтээр тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
