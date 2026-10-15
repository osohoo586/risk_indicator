/*---
indicator_id: RI_04_0153
name_mn: "Дилерийн арилжааны лимит зөрчсөн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-2 удаа зөрчсөн
  3-1 удаа зөрчсөн
  0-Зөрчөөгүй
source_system: "ЗЗЭУХ, НУГ-АХ, СУГ-Метрик үзүүлэлт"
required_info: "Арилжааны лимит зөрчсөн тоо"
method: "ЭУГ-ЗЗЭУХ-ээс мэдээлэл авч лимит зөрчсөн тоогоор үнэлнэ."
period_text: "Сүүлийн 1 жилд"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
