/*---
indicator_id: RI_18_0681
name_mn: "Нийт харилцагчийн тоо - Голомт банкаар цалингаа авдаг харилцагч /ОН/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ИБГ-БХ"
required_info: "ST7020"
method: |
  ОН: Сүүлийн 3 сард хамгийн багадаа 1 удаа цалингаа авсан харилцагчийн тоо
  - Sal цэсээр цалин тавигдсан
  - Цалин, сүүл цалин, урьдчилгаа гэсэн утгатай орлого хүлээж авсан
  - БТГ-ийн цалингийн гүйлгээ /төрийн/
  - Интернет банкны payroll цэсээр цалин тавигдсан
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
