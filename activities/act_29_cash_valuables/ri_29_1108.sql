/*---
indicator_id: RI_29_1108
name_mn: "Бүртгэгдсэн илүүдэл, дутагдлын давтамж их байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-120 ба түүнээс дээш
  4-91-120 удаа
  3-61-90 удаа
  2-31-60 удаа
  1-1-30 удаа
source_system: "КҮЗХ"
required_info: "Илүүдэл дутагдлын бүртгэл"
method: "Тоолох тасгийн тоолсон мөнгөнөөс сарын дунджаар тооцох, БОМ-ын зуз, салбар нэгжийн зуз, харилцагчийн тушаасан цүхнтэй мөнгөний данс, ностро зузын дансдыг үзэх"
period_text: "Аудит орсноос сарын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
