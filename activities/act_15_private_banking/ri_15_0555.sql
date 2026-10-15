/*---
indicator_id: RI_15_0555
name_mn: "Хүүгийн зардал - Бодит хүү"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-3.1% болон түүнээс дээш
  4-2.6-3.0%
  3-2.1-2.5%
  2-1.6-2.0%
  1-1.5%-аас бага
source_system: "ИБГ-ХБХ"
required_info: "Төлөвлөгөөний биелэлт"
method: "Тоон төлөвлөгөөний биелэлтээр тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
