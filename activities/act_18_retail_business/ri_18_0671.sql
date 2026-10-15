/*---
indicator_id: RI_18_0671
name_mn: "Нийт харилцах, хадгаламжийн хэмжээ - ОН"
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
method: "Нийт ОН салбарын нийт харилцах, хадгаламжийн дүн / Зөвхөн СТТ-н R CIF-тэй эх үүсвэрийн гүйцэтгэл орно/"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
