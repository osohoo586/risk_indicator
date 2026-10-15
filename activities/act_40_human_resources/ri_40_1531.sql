/*---
indicator_id: RI_40_1531
name_mn: "ХНХ-ны шийдвэрийн хэрэгжилтийг хянаж, тайлагнадаг эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Шийдвэрийн хэрэгжилтийг хагас жилд 1 удаа танилцуулдаг
  3-Шийдвэрийн хэрэгжилтийг  жилд 1 танилцуулдаг
  5-Шийдвэрийн хэрэгжилтийг танилцуулаагүй
  0-Үнэлэхгүй
source_system: "ХНХ-ны нарийн бичиг"
required_info: "ХНХорооны шийдвэрийн хэрэгжилт"
method: "ХНХорооны шийдвэрийн хэрэгжилтэд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
