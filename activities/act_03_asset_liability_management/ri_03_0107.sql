/*---
indicator_id: RI_03_0107
name_mn: "Хүүд мэдрэмжтэй актив, пассивын зөрүү"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5- +200%-с дээш, -200% доош
  4- +200%-тай тэнцүү, -200%-тай тэнцүү
  3- +190 < > -190
  2- +180 < > -180
  1- +170 < > -170
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "Хүүд мэдрэмжтэй актив, пассивын зөрүү/ӨХ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
