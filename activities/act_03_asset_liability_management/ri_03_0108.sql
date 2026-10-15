/*---
indicator_id: RI_03_0108
name_mn: "Зээл депозитын харьцаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-68%-аас дээш
  4-0.68
  3-66-67.9%
  2-64-65.9%
  1-64%-аас доош
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: |
  Зээлтэй адилтгах актив/Депозит
  Өөрийн хөрөнгийн
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
