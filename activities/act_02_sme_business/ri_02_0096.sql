/*---
indicator_id: RI_02_0096
name_mn: "Банкны системд эзлэх хувь - SME зээлийн хэмжээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 5                       # үйл ажиллагаа доторх жин (%)
score_type: "score5"
scale_text: |
  1-Зах зээлд эзлэх хувь өссөн. Зорилтод хүрсэн
  2-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрсэн
  3-Зах зээлд эзлэх хувь хувь өссөн. Зорилтод хүрээгүй
  5-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрээгүй
source_system: "BI тайлангийн систем"
required_info: "Төлөвлөгөөний гүйцэтгэл"
method: "ББГ сегментийн зээлийн үлдэгдэл / Системийн нийт байгууллагын (SME) зээлийн үлдэгдэл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
