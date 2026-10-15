/*---
indicator_id: RI_29_1109
name_mn: "Бүртгэгдсэн хүчингүй, хуурамч дэвсгэртийн давтамж их байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-15-аас дээш удаа
  4-11-15 удаа
  3-6-10 удаа
  2-1-5 удаа
  1-Хүчингүй, хуурамч дэвсгэрт гараагүй.
source_system: "КҮЗХ"
required_info: "Хүчингүй хуурамч дэвсгэртйин бүртгэл"
method: "Тоолох тасгийн тоолсон мөнгөнөөс сарын дунджаар тооцох, БОМ-ын зуз, салбар нэгжийн зуз, харилцагчийн тушаасан цүхнтэй мөнгөний данс, ностро зузын дансдыг үзэх"
period_text: "Аудит орсноос сарын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
