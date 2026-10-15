/*---
indicator_id: RI_20_0752
name_mn: "ҮАЗ гүйцэтгэл - АТМ-н автоматжуулалт, тоног төхөөрөмж"
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
source_system: "BI"
required_info: "Төлөвлөгөөний гүйцэтгэл"
method: "Тайлант хугацааны худалдан авалтын төлөвлөгөө, биелэлт"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
