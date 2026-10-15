/*---
indicator_id: RI_35_1329
name_mn: "Автомат бус зээлийн судалгааны хурд"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-1-3 хоногт
  3-3-4 хоногт
  5-4-өөс дээш хоногт
source_system: "ЗГ, СУГ"
required_info: "Зээлийн судалгааны хурдыг хэмжсэн тайлан"
method: "Нийт судлагдсан зээлийн хэдэн хувь нь стандарт хугацааг хангасан эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж хугацаагаар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
