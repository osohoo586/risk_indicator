/*---
indicator_id: RI_32_1222
name_mn: "Зохион байгуулсан маркетингийн кампейний төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "МХ"
required_info: "Зохион байгуулсан campaign-ий биелэлт"
method: "Зохион байгуулахаар төлөвлөсөн кампейний төлөвлөгөөний биелэлтэд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
