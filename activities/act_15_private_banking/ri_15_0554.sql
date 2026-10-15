/*---
indicator_id: RI_15_0554
name_mn: "Нийт картын тоо - Премьер дебит /ВИП карт/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ИБГ-ХБХ"
required_info: "Төлөвлөгөөний биелэлт"
method: "Тоон төлөвлөгөөний биелэлтээр тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
