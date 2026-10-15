/*---
indicator_id: RI_04_0151
name_mn: "Маржин арилжаанаас алдагдал хүлээсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Алдагдал хүлээсэн
  1-Алдагдал хүлээгээгүй
  0-Арилжаа хийгээгүй
source_system: "НУГ-АХ"
required_info: "Маржин арилжааны мэдээлэл"
method: "НУГ-АХ-ээс авсан мэдээлэлд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
