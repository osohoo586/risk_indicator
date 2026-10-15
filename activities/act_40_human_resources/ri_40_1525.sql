/*---
indicator_id: RI_40_1525
name_mn: "Албан тушаалд томилол сонгон шалгаруулалтын дундаж хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Ажлын 24 хоногоос бага хугацаанд
  2-Ажлын 24-26 хоногт
  3-Ажлын 27-29 хоногт
  4-Ажлын 30 хоногт
  5-Ажлын 30-аас дээш хоногт
source_system: "ХНУГ"
required_info: "Сонгон шалгаруулалтын хугацаа"
method: "Сонгон шалгаруулалтын дундаж хугацаанд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
