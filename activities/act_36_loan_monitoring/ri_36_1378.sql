/*---
indicator_id: RI_36_1378
name_mn: "Watchlist жагсаалтын зээлийн багц өсөх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Дүн болон тоо өссөн, нэгдсэн бүртгэлгүй
  4-Дүн өссөн тоо буурсан
  3-Дүн буурсан тоо өссөн
  1-Дүн буурсан тоо буурсан
source_system: "ЭУГ-ЗЭУХ, ДАГ-ЗАЧБХ"
required_info: "Watchlist бүртгэлтэй зээлийн жагсаалт"
method: "Нийт зээлийн үлдэгдэл тоог өмнөх жилтэй харьцуулж үнэлэх"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
