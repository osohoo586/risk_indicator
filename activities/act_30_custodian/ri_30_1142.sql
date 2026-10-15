/*---
indicator_id: RI_30_1142
name_mn: "Програмын эрхийн матриц зөрчигдсөн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Эрхийн матрицын хэрэгжилтэд хяналт тавьдаггүй, эсвэл зөрчил гарсан тохиолдол бүртгэгдсэн.
  0-Хоцроосон тохиолдол гараагүй
source_system: "Кастодиан банк"
required_info: "ҮЦЗЗ дээр ажиллах, гүйлгээ хийх эрхийн матриц зөрчигдсөн эсэх"
method: "Банкны үндсэн програм бус ҮЦЗЗ дээр ажилладаг тусдаа програмын эрхийн матрицын хэрэгжилтэд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
