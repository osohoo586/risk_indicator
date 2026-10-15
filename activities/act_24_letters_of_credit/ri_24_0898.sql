/*---
indicator_id: RI_24_0898
name_mn: "Гараар бэлтгэж буй тайлан байдаг эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-3-с олон тайлан бэлтгэдэг, гараар бэлтгэсэн тайлан алдаатай гарсан. /зөрүүтэй/
  4-3 тайлан бэлтгэдэг
  3-2 тайлан бэлтгэдэг
  2-1 тайлан бэлтгэдэг
  1-Байхгүй
source_system: "БТГ-АХ"
required_info: "Нэгжээс тодруулах"
method: "Нэгжээс гараар бэлтгэдэг тайлангийн тоог тодруулах"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
