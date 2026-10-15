/*---
indicator_id: RI_35_1327
name_mn: "Тогтмол орлоготой орон сууцны зээлийн судалгааны хурд"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-90.1%-92.9%
  3-93%-95.9%
  2-96%-97.9%
  1-98-100%
source_system: "ЗГ, СУГ"
required_info: "Зээлийн судалгааны хурдыг хэмжсэн тайлан"
method: |
  Судалгааны хурдны дундаж хугацаа нь ЗҮАЖ-д заасан хугацааны шаардлагад хүрч байгаад үндэслэн дүгнэнэ
  Хугацаандаа хийгдсэн судалгааны тоо/Нийт судалгааны тоо
period_text: "Аудит орсноос хойш улирлын дундаж хугацаагаар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
