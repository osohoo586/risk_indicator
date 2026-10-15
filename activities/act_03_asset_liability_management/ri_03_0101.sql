/*---
indicator_id: RI_03_0101
name_mn: "1-р зэрэглэлийн өөрийн хөрөнгийн хүрэлцээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-14.5% болон түүнээс дээш
  2-13.8%-14.4%
  3-12.9%-13.7%
  4-12%-12.8%
  5-12%-с доош
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "1-р зэрэглэлийн өөрийн хөрөнгийн/Эрсдэлээр жигнэсэн актив"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
