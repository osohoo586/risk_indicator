/*---
indicator_id: RI_28_1068
name_mn: "Голомт банкны төхөөрөмжид луйвар, залилангийн гүйлгээ гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Луйвар гарсан
  0-Луйвар гараагүй
source_system: "ДБГ-ЦХАХ"
required_info: "Луйвар, залилан гарсан эсэх мэдээлэл"
method: "Аудит орсноос хойш голомт банкны төхөөрөмжид луйвар залилангийн хэрэг гарсан эсэх мэдээлэлд үндэслэн үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
