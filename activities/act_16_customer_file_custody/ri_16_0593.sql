/*---
indicator_id: RI_16_0593
name_mn: "Jira хүсэлтийн дагуу архиваас баримт олдохгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Зөрчил гараагүй
  5-Зөрчил гарсан
source_system: "ХБГ-АЛА"
required_info: "Архивын хүсэлт"
method: "- Жира хүсэлтээр ирүүлсэн баримт архиваас олдоогүй тохиолдол гарсан эсэх"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
