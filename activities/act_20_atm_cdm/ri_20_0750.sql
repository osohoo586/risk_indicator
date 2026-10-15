/*---
indicator_id: RI_20_0750
name_mn: "Голомт банкны системийн алдаанаас үүссэн маргаантай гүйлгээний тоо өсөх.  АТМ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Нийт гүйлгээний 0.1%-с хэтэрсэн.
  4-Нийт гүйлгээний 0.08-0.099%
  3-Нийт гүйлгээний 0.06-0.079%
  2-Нийт гүйлгээний 0.04-0.059%
  1-Нийт гүйлгээний 0.04%-аас бага
source_system: "JIRA"
required_info: "Маргаантай гүйлгээний мэдээлэл"
method: "Нийт маргаантай гүйлгээ/Нийт гүйлгээ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
