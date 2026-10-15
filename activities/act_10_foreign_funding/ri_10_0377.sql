/*---
indicator_id: RI_10_0377
name_mn: "Банкны гадаад сурталчилгаанд зориулж зохион байгуулсан ажлууд байгаа эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Байхгүй
  4-1 удаа хийсэн
  3-2 удаа хийсэн
  2-3 удаа хийсэн
  1-4-с олон удаа хийсэн
source_system: "BI"
required_info: "Сурталчилгааны ажлын мэдээлэл"
method: "Нэгжээс авсан мэдээллийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
