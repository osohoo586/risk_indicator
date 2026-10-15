/*---
indicator_id: RI_08_0307
name_mn: "Western union засварын гүйлгээний жира"
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
  1-1
source_system: "JIRA систем"
required_info: "Засвар хийсэн огнооны мэдээ"
method: |
  Засварын гүйлгээг хийсэн хугацаа
  Тухайн өдөрт нь хийсэн засвар/Нийт засвар
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
