/*---
indicator_id: RI_10_0379
name_mn: "Гадаад төлбөр тооцооны зах зээлд эзлэх хувь /илгээсэн дүнгээр/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-20%-аас бага
  3-21-25%
  1-26%-аас дээш
source_system: "BI"
required_info: "ST7020"
method: "Тухайн хугацаанд илгээсэн нийт гадаад гуйвуулгын дүнгээр системд эзлэх хувь /Swift-н тайлангаар/"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
