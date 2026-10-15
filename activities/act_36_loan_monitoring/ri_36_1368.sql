/*---
indicator_id: RI_36_1368
name_mn: "Чанаргүй зээлийн нийт зээлийн багцад эзлэх хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-5% түүнээс дээш
  4-0.05
  3-4-4.9%
  2-3-3.9%
  1-3%-аас бага
source_system: "BI"
required_info: "Зээлийн дэлгэрэнгүй тайлан, кредит картын дэлгэрэнгүй тайлан"
method: "Банкны лимит, зорилт, хязгаарлалтуудад үндэслэн дүгнэнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
