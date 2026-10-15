/*---
indicator_id: RI_16_0590
name_mn: "Эрх бүхий байгууллагын шийдвэрийн дагуу битүүмж тавих, чөлөөлөх бүртгэлийг цаг тухайд нь хийгээгүй улмаас зөрчил гарсан эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчил гарсан
  0-Зөрчил гараагүй
source_system: "ХБХХ"
required_info: "Хүсэлт шийдвэрлэсэн мэдээлэл"
method: "Нийт хүсэлтийг шийдвэрлэсэн байдлыг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
