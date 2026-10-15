/*---
indicator_id: RI_03_0112
name_mn: "Хадгаламжийн төвлөрлийн харьцаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-22%-аас доош
  2-22%-22.9%
  3-23%-23.9%
  4-24%-24.9%
  5-25% болон түүнээс дээш
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "TOP 10 харилцагчийн хадгаламж/Нийт актив"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
