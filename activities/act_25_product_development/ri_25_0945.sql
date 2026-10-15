/*---
indicator_id: RI_25_0945
name_mn: "Парамертийн тохиргооны жира хүсэлт шийдвэрлэсэн байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-1 хоног дотор
  3-2-3 хоног
  5-3-аас дээш хоног
source_system: "JIRA"
required_info: "Параметрийн тохиргоо хийсэн мэдээлэл"
method: "Шийдвэрлэсэн жираг нийт жираны тоонд харьцуулж тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
