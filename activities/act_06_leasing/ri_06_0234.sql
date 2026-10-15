/*---
indicator_id: RI_06_0234
name_mn: "Стандарт хугацаанд хүсэлт шийдвэрлэсэн хувь - Жижиг санхүүгийн түрээс"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-75% ба түүнээс доош
  4-74.9%-84.9%
  3-85%-89.9%
  2-90%-95.9%
  1-95-100%
source_system: "ЗГ-ЗМХ"
required_info: "ЗГ-ЗМХ-с хэрэгжүүлсэн хяналт хийсэн мэдээлэлд үндэслэн дүгнэнэ."
method: "500-2 тэрбум₮ хүртэл харилцагчийн хүсэлтийг хугацаанд судалсан байдал - ажлын 18 цаг"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
