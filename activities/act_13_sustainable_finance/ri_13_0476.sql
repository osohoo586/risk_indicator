/*---
indicator_id: RI_13_0476
name_mn: "ОУ-ын байгууллагын магадлан шинжилгээг гүйцэтгэсэн тоо - БОНЗ DD/KYC"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "BI"
required_info: "Төлөвлөгөөний биелэлтийн хувь"
method: "Тухайн хугацаанд тогтвортой хөгжлийн чиглэлээр гүйцэтгэсэн DD/KYC тоо /өссөн/"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
