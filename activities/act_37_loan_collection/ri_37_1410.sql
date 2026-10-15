/*---
indicator_id: RI_37_1410
name_mn: "ТАХ-т бүртгэлтэй зээлийн бууралт\nЗээлийн багц/ТАХ/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Өссөн
  4-Өөрчлөлт гараагүй
  3-Буурсан
source_system: "BI"
required_info: "Зээлийн дэлгэрэнгүй тайлан"
method: "ТАХ-д бүртгэлтэй зээлийн багцыг аудит орсноос хойш хугацаанд буурсан эсэхэд үндэслэж үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
