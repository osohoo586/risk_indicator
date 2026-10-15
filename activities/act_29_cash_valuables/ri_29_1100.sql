/*---
indicator_id: RI_29_1100
name_mn: "Хамгаалалтын гэрээт байгууллагын гэрээгээр хүлээсэн үүргийг дүгнэдэг эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчил, гомдол 3-аас дээш удаа гарсан
  4-Зөрчил, гомдол 3 удаа гарсан
  3-Зөрчил, гомдол 2 удаа гарсан
  2-Зөрчил, гомдол 1 удаа гарсан
  1-Зөрчил, гомдол гараагүй
source_system: "КҮЗХ"
required_info: "ГХХ-ын зөрчлийн мэдээлэл"
method: "Хамгаалалтын байгууллагаас шалтгаалан зөрчил гомдол гарсан эсэхийг КҮЗХ-ээс мэдээлэл авах"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
