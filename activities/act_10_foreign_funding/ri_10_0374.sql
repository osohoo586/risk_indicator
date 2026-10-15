/*---
indicator_id: RI_10_0374
name_mn: "Шинээр нээсэн болон нэмэгдүүлсэн санхүүжилт болон санхүүжилтийн төрөл бүрийн шугамын хэмжээ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Буурсан
  3-Өөрчлөлтгүй
  1-Өссөн
source_system: "СБХ"
required_info: "Шинээр нээсэн санхүүжилтийн мэдээлэл"
method: "Нэгжээс авсан мэдээллийг харгалзан үнэлнэ"
period_text: "Өмнөх улиралтай харьцуулах"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
