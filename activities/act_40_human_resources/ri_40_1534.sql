/*---
indicator_id: RI_40_1534
name_mn: "C suite болон бодлогын нэгжүүдиийн захирлуудын орон тоо сул байсан хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-5 хоног
  2-6 - 10 хоног
  3-11- 20 хоног
  4-21-30 хоног
  5-30 хоногоос дээш
source_system: "ХНУГ"
required_info: "Орон тоо сул байсан хугацаа"
method: "Аудит орсноос хойш орон тоо сул байсан албан тушаалтнуудын дундаж хугацаагаар хэмжинэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
