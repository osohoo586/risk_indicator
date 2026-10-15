/*---
indicator_id: RI_37_1412
name_mn: "Нийт зээлийн хүүг чөлөөлж хөнгөлсөн тохиолдлын тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Шаардлага хангаагүй зээлийн хүүг чөлөөлсөн
  4-Тохиолдол гарсан
  1-Тохиолдол гараагүй.
source_system: "ТАХ"
required_info: "Хүү чөлөөлсөн зээлийн мэдээлэл"
method: "ТАХ-ээс хүү чөлөөлсөн зээлийн мэдээллийг авч үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
