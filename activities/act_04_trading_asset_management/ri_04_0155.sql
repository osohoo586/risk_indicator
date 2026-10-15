/*---
indicator_id: RI_04_0155
name_mn: "Валют арилжааны эргэлтийн хэмжээний төлөвлөгөөний биелэлт"
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
source_system: "НУГ-АХ, СУГ-Метрик үзүүлэлт"
required_info: "Валют арилжааны эргэлтийн дүн"
method: "Тайлант хугацаанд банкны хэмжээнд хийгдсэн нийт валют арилжааны эргэлтийн дүн, төгрөгөөр"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
