/*---
indicator_id: RI_16_0592
name_mn: "Архиваас баримт авах хүсэлтийг шийдвэрлэсэн хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Ажлын 1-4 хоногийн дотор шийдвэрлэсэн
  3-Ажлын 5 хоногт шийдвэрлэсэн
  5-5-аас дээш хоногийн дараа шийдвэрлэсэн
source_system: "ХБГ-АЛА"
required_info: "Sboarchive, Archiveref прожектоор оруулсан хүсэлтийг"
method: "JIRA Project-оос хүсэлт үүсгэснээс шийдвэрлэсэн хүртэлх хугацааг хэмжиж үнэлнэ"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
