/*---
indicator_id: RI_37_1414
name_mn: "ХМА-ны хариуцсан зээлийн багцын бууралт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Өссөн
  3-Өөрчлөлт гараагүй
  1-Буурсан
source_system: "ХМА"
required_info: "Зээлийн дэлгэрэнгүй тайлан"
method: "Өмнөх аудит орсноос хойш гарсан өөрчлөлтөд үндэслэн дүгнэнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
