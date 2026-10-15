/*---
indicator_id: RI_03_0106
name_mn: "Богино хугацаат актив пассивын харьцаа 6 сар"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90%-с бага эсвэл 110%-с их
  4-90% эсвэл 110%
  3-90%-110%
  2-93-107%
  1-95-105%
source_system: "НУГ-АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "Богино хугацаат актив пассивын харьцаа 6 сар"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
