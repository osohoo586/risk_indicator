/*---
indicator_id: RI_40_1527
name_mn: "Хүний нөөцтэй холбоотой жира хүсэлт хугацаандаа шийдэгдээгүй тохиолдлын хувь."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "JIRA"
required_info: "JIRA- Цалингийн бодолт засуулах хүсэлт болон бусад шалгуулах хүсэлт"
method: "Өмнөх улиралтай харьцуулж үнэлэх"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
