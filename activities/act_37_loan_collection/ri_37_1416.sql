/*---
indicator_id: RI_37_1416
name_mn: "МИК-д зээл борлуулсан хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-60%-аас бага
  4-60%-69%
  3-70%-79%
  2-80%-89%
  1-90%-иас дээш
source_system: "ИБГ-МИК"
required_info: "МИК-д зээл борлуулсан гүйцэтгэлийн мэдээлэл"
method: "Борлуулсан/Борлуулах зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
