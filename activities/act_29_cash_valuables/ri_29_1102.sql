/*---
indicator_id: RI_29_1102
name_mn: "Өндөр дүнтэй хуурамч, хүчингүй мөнгө бүртгэгдэх. Монгол банкинд тушаасан мөнгөнөөс"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-1,000,000 төгрөгөөс дээш
  4-800,000-999,999 төгрөг
  3-600,000-799,999 төгрөг
  2-0-599,999 төгрөг
  1-Хуурамч мөнгө илрээгүй
source_system: "КҮЗХ"
required_info: "КҮЗХ-ийн хуурамч хүчингүй мөнгөний бүртгэл"
method: "Монголбанканд тушаасан мөнгөнөөс хуурамч, хүчингүй мөнгө илэрсэн тохиолдлыг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
