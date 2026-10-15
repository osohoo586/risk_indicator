/*---
indicator_id: RI_03_0103
name_mn: "TOP 10 харилцагчийг хасч тооцсон ТТГЧ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-18%-аас доош
  4-18-20%
  3-21-23%
  2-24-25%
  1-25%-аас дээш
  0-Үнэлэхгүй
source_system: "АПУХ, ДАГ-ЗАЧБХ"
required_info: "PR-тайлан, Хугацаа хоцрогдолтой тохиолдолд СУГ-ын метрик үзүүлэлтээр үнэлж болно."
method: "Түргэн борлогдох хөрөнгө/Бусдаас татан төвлөрүүлсэн хөрөнгө"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
