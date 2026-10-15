/*---
indicator_id: RI_40_1536
name_mn: "Career path index"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-28-29.9%
  2-26-27.9%
  3-23-26.9%
  4-20.1-22.9%
  5-20%-аас бага, 30%-аас их
source_system: "ХНУГ"
required_info: "Ажилтнуудын шилжилт хөдөлгөөний мэдээлэлл"
method: "Тушаал дэвшсэн ажилтан / (Тушаал дэвшсэн+албан тушаал солигдсон буюу хөндлөн шилжилтэ хийсэн)"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
