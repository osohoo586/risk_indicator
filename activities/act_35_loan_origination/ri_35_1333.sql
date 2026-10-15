/*---
indicator_id: RI_35_1333
name_mn: "Иргэдийн зээлийн хороо эрхээ хэтрүүлж зээлийн шийдвэр гаргасан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчил гарсан
  0-Зөрчил гараагүй
source_system: "ДАГ, ЗГ-ЗБХ"
required_info: "Эрх хэтрүүлж зээл олгосон эсэх мэдээлэл"
method: "Дотоод аудитын баталгаажуулалтын үр дүн эсвэл ЗГ-ЗБХ-МА-ийн мониторингийн хэлтсийн үр дүнд хороодын матриц зөрчсөн эсэхийг харгалзан үнэлнэ үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
