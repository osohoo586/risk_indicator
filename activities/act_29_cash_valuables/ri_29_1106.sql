/*---
indicator_id: RI_29_1106
name_mn: "Салбар тооцооны төвийн зузаатгалын хүсэлтийг шийдвэрлэсэн байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Ажлын 9-10 цагт
  3-Ажлын 7-8 цагт
  1-Ажлын 6 цаг дотор
source_system: "JIRA"
required_info: "Хүсэлт шийдвэрлэсэн хугацаа"
method: "JIRA хүсэлтийн шийдвэрлэсэн хугацаагаар хэмжинэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
