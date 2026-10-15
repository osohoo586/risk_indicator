/*---
indicator_id: RI_29_1098
name_mn: "Мөнгөн зөөврийн албаны ажилтнуудыг даатгалд хамруулсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Даатгалд хамрагдаагүй ажилтан байгаа
  4-85-89% даатгалд хамрагдсан
  3-90-94% даатгалд хамрагдсан
  2-95-99% даатгалд хамрагдсан
  1-100% даатгалд хамрагдсан
source_system: "КҮЗХ"
required_info: "Даатгалд хамруулсан ажилтны жагсаалт"
method: "Нийт мөнгөн зөөврийн албаны ажилтнууд амь насны даатгалд хамрагдсан эсэхийг баталгаажуулна."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
