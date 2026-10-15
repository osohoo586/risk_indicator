/*---
indicator_id: RI_36_1367
name_mn: "Анхаарал хандуулах зээлийн нийт зээлийн багцад эзлэх хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-2.5% ба түүнээс бага
  2-2.5%-3.9%
  3-4%-5.4%
  4-5.5%-6.9%
  5-7% ба түүнээс дээш
source_system: "BI"
required_info: "Зээлийн дэлгэрэнгүй тайлан, кредит картын дэлгэрэнгүй тайлан"
method: "Банкны лимит, зорилт, хязгаарлалтуудад үндэслэн дүгнэнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
