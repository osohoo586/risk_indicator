/*---
indicator_id: RI_16_0598
name_mn: "Ложистикийн тээвэрлэлтийн үед баримт, хувийн хэрэг алдагдсан тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Гараагүй
  5-Гарсан
source_system: "ХБГ-АЛА"
required_info: "Ложистикийн зөрчлийн мэдээлэл"
method: "Тээвэрлэлтийн үеэр салбарын хувийн хэрэг, баримт алга болсон зөрчил гарсан эсэх."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
