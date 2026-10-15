/*---
indicator_id: RI_26_0977
name_mn: "Шинэ бүтээгдэхүүн, модуль нэвтэрсэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Тийм
  3-Сайжруулалт хийсэн
  1-Үгүй
source_system: "ДБХ"
required_info: "ДБХ-ийн бүтээгдэхүүний мэдээлэл"
method: "Сайжруулсан болон шинэ бүтээгдэхүүн байгаа эсэхийг харгалзан үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
