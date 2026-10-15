/*---
indicator_id: RI_13_0475
name_mn: "Банкны нийт зээлийн багцад эзлэх ногоон зээлийн хувь хэмжээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "BI"
required_info: "Зээлийн төлөвлөгөөний биелэлт"
method: "(МБ уруу тайлагнасан ногоон зээлийн багцын хэмжээ) / (Нийт Банкны зээлийн багц)"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
