/*---
indicator_id: RI_24_0896
name_mn: "Аккредитивийн төлбөр цаг хугацаандаа хийгдсэн байдал."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хугацаа хэтэрсэн тохиолдол гарсан
  1-Хугацаа хэтэрсэн тохиолдол гараагүй
source_system: "БТГ-АХ"
required_info: "Төлбөр хийгдсэн мэдээлэл"
method: "Хугацаа хэтэрч хийгдсэн төлбөр байгаа эсэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
