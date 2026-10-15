/*---
indicator_id: RI_35_1330
name_mn: "Эрсдэлийн дүгнэлт гаргах хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-4 хоногт
  2-5 хоногт
  3-6 хоногт
  4-7 хоногт
  5-7 хоногоос дээш
source_system: "ЗГ, СУГ"
required_info: "Эрсдэлийн дүгнэлт гарсан хурдыг хэмжсэн тайлан"
method: "Эрсдэлийн дүгнэлтийн  хурдны дундаж хугацаа нь ЗҮАЖ-д заасан хугацааны шаардлагад хүрч байгаад үндэслэн дүгнэнэ"
period_text: "Аудит орсноос хойш улирлын дундаж хугацаагаар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
