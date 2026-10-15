/*---
indicator_id: RI_27_1010
name_mn: "Идэвхтэй картын зах зээлд эзлэх хувь буурах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Зах зээлд эзлэх хувь өссөн. Зорилтод хүрсэн
  2-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрсэн
  3-Зах зээлд эзлэх хувь хувь өссөн. Зорилтод хүрээгүй
  5-Зах зээлд эзлэх хувь буурсан. Зорилтод хүрээгүй, зорилтгүй
source_system: "КХ, СУГ-Метрик"
required_info: "Картын зах зээлд эзлэх хувь"
method: "Голомт банкны идэвхитэй картын тооны зах зээлд эзлэх хувьд үндэслэнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
