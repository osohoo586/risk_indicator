/*---
indicator_id: RI_10_0375
name_mn: "Гадаад дахь банкны төлөөлөгчийн газрын үйл ажиллагаанд хяналт тавьж буй байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хяналт тавих тогтолцоо байхгүй
  3-Бүрэн хяналт тавьж чаддаггүй
  1-Хяналт бүрэн тавьж чаддаг
source_system: "СБХ"
required_info: "Гадаад дахь банкны төлөөлөгчийн газар хийсэн хяналтын мэдээ"
method: "Нэгжээс авсан мэдээллийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
