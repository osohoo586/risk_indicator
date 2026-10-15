/*---
indicator_id: RI_23_0864
name_mn: "Банкинд ирсэн гомдлыг камерын чанар хангалтгүйгээс шийдвэрлээгүй тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Гарсан
  0-Гараагүй
source_system: "ДАГ, ХҮГ"
required_info: "Гомдлын мэдээлэл"
method: "Хяналтын камерын бичлэг нь харилцагчийн гомдлыг шийдвэрлэхэд шаардлага хангахгүй тохиолдол гарсан эсэхийг дүгнэнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
