/*---
indicator_id: RI_37_1415
name_mn: "Зээлийн хэрэг бүртгэлтэй холбоотой зөрчил"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ЗГ-МХ"
required_info: "ЗГ-Мониторингийн хэлтсийн хяналтын үр дүн"
method: "МХ-ийн үр дүнд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш улирал бүрийн дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
