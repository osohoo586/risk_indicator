/*---
indicator_id: RI_35_1338
name_mn: "Зээлийн хэрэг бүртгэлийн чанар"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ЗГ-ЗБХ-МА"
required_info: "ЗГ-ЗБХ-МА-ийн зөрчлийн мэдээлэл"
method: "Зөрчлийн мэдээлэл"
period_text: "Аудит орсноос хойш улирлын дундаж мэдээлэл"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
