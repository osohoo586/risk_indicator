/*---
indicator_id: RI_18_0672
name_mn: "Шимтгэл хураамжийн орлого - Салбар"
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
source_system: "BI"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: |
  Нийт салбарын нийт шимтгэл хураамжийн орлогын төлөвлөгөө, гүйцэтгэл.
  - Дансны шимтгэлийн орлого
  - Картын шимтгэл
  - Гуйвуулгын шимтгэл хураамжийн орлого
  - Хэрэглээний зээлийн шимтгэл
  - Дижитал бүтээгдэхүүн, сувгийн шимтгэл
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
