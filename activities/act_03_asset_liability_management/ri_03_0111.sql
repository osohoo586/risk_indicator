/*---
indicator_id: RI_03_0111
name_mn: "Цэвэр хүүгийн ахиуц"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-3.2%-с доош
  4-3.2%-3.29%
  3-3.3%-3.39%
  2-3.4%-3.49%
  1-3.5%-аас дээш
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "(Хүүгийн орлого-Хүүгийн зардал)/Орлого олдог актив"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
