/*---
indicator_id: RI_10_0376
name_mn: "Хийгдсэн Due dilligence-н тоо."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хийгээгүй
  4-1 удаа хийсэн
  3-2 удаа хийсэн
  2-3 удаа хийсэн
  1-4-с олон удаа хийсэн
source_system: "СБХ"
required_info: "Хийгдсэн Due dilligence-н тоо."
method: "Нэгжээс авсан мэдээллийг харгалзан үнэлнэ. Үнэлгээний чанар"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
