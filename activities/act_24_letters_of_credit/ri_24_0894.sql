/*---
indicator_id: RI_24_0894
name_mn: "Аккредитивын хэмжээгээр банкны системд эзлэх хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Зах зээлд эзлэх хувь өссөн. Зорилтод хүрсэн
  2-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрсэн
  3-Зах зээлд эзлэх хувь хувь өссөн. Зорилтод хүрээгүй
  5-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрээгүй, зорилтгүй
source_system: "ОУБГ"
required_info: "Аккредитивын хэмжээгээр банкны системд эззлэх хувь."
method: "Зах зээлд хувийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
