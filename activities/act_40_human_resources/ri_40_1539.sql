/*---
indicator_id: RI_40_1539
name_mn: "Шаардлагатай албан тушаалд бэлтгэсэн нөөцийн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Нөөцийн үлдэгдэлтэй
  5-Нөөцийн үлдэгдэлгүй
source_system: "ХНУГ"
required_info: "Нөөцийн тоо"
method: "Бэлтгэх сургалтад хамрагдаж тэнцсэн оролцогчийн тоо /өссөн дүнгээр/"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
