/*---
indicator_id: RI_34_1296
name_mn: "Төслийн удирдагч хангалтгүй үнэлэгдэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хангалтгүй үнэлгээ авсан удирдагч байгаа
  1-Хангалтгүй үнэлгээ авсан удирдагч байхгүй
source_system: "ДШГ-ТУХ"
required_info: "ДШГ-ТУХ-с мэдээлэл авах"
method: "Төслийн удирдагч нь ДШГ-ТУХ-с хангалтгүй үнэлгээ авсан эсэхийг шалгах"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
