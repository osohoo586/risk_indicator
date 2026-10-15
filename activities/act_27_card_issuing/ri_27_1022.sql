/*---
indicator_id: RI_27_1022
name_mn: "Картын пластикийн нөөцөөс дуусч тасалдал үүссэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчил гарсан
  0-Зөрчил гараагүй
source_system: "КХ"
required_info: "Картын пластикийн тасалдал үүссэн эсэх"
method: "Картын пластикийн тасалдал үүссэн эсэхийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
