/*---
indicator_id: RI_16_0591
name_mn: "Зөвшөөрлөөр олгосон архивын баримтыг заагдсан хугацааны дотор эргэн авчраагүй."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-30 хоногийн дотор буцаан авсан
  3-30 хоногоос хэтрүүлж буцаасан тохиолдол гарсан
  5-Буцааж баримтаа аваагүй тохиолдол гарсан тохиолдол гарсан.
source_system: "ХБГ-АЛА"
required_info: "Архивын баримт ашиглах жира хүсэлт"
method: "Архивын баримт эргэн авчирсан хугацаа"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
