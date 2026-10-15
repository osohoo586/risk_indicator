/*---
indicator_id: RI_21_0789
name_mn: "RPA ашиглаж хүн/цаг хэмнэсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Хэмнэсэн хүн/цаг өссөн. Зорилтод хүрсэн
  2-Хэмнэсэн хүн/цаг буурсан. Зорилтод хүрсэн
  3-Хэмнэсэн хүн/цаг өссөн. Зорилтод хүрээгүй
  5-Хэмнэсэн хүн/цаг буурсан. Зорилтод хүрээгүй
source_system: "ДШГ-ПУХ"
required_info: "RPA ашиглан хэмнэсэн хүн/цаг"
method: "ДШГ-ПУХ-с ирүүлсэн RPA ашиглан нийт хэмнэсэн хүн/цаг-н тоон мэдээлэл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
