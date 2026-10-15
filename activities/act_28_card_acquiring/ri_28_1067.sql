/*---
indicator_id: RI_28_1067
name_mn: "Голомт банкны системийн алдаанаас үүссэн маргаантай гүйлгээний тоо өсөх. КҮБ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Нийт гүйлгээний 0.1%-аас хэтэрсэн
  4-Нийт гүйлгээний 0.08-0.099%
  3-Нийт гүйлгээний 0.06-0.079%
  2-Нийт гүйлгээний 0.04-0.059%
  1-Нийт гүйлгээний 0.04%-аас бага
source_system: "JIRA"
required_info: "Маргаантай гүйлгээний мэдээлэл"
method: "Нийт маргаантай гүйлгээ/Нийт гүйлгээ"
period_text: "Аудит орсноос хойш хугацаанд улирлыын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
