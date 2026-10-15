/*---
indicator_id: RI_37_1411
name_mn: "ТАХ-т бүртгэлтэй зээлүүдийг сангаас хаах байдлаар шийдвэрлэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Шаардлага хангаагүй зээлийг сангаас хаасан
  4-Сангаас хаасан тохиолдол гарсан
  1-Тохиолдол гараагүй.
source_system: "ТАХ, PR тайлан харах"
required_info: "Сангаас хаасан зээлийн мэдээлэл"
method: "ТАХ-ээс сангаас хаасан зээлийн мэдээллийг авч үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
