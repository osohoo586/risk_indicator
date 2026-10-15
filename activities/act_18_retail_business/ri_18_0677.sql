/*---
indicator_id: RI_18_0677
name_mn: "Нийт харилцагчийн тоо - Alpha, GEN-Z (0-28 насны) сегмент"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ИБГ-БХ"
required_info: "Харилцагчийн мэдээлэл"
method: "Тайлант хугацааны эцэст 0-26 насны буюу 1996/01/01-с хойш төрсөн данс нь устаагүй, зээл харилцах, хадгаламжийн аль нэг данстай иргэн харилцагчийн тоо /R-CIF/"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
