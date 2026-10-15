/*---
indicator_id: RI_04_0152
name_mn: "Гадаад валютын ханшийн эрсдэлийн VAR лимит зөрчсөн тоо"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрчсөн 3-аас дээш тохиолдол гарсан
  4-Зөрчсөн 3 тохиолдол гарсан
  3-Зөрчсөн 2 тохиолдол гарсан
  2-Зөрчсөн 1 тохиолдол гарсан
  0-Хамрах хугацаанд лимит зөрчөөгүй
source_system: "ЗЗЭУХ,  НУГ-АХ"
required_info: "VAR лимит зөрчсөн эсэх мэдээлэл"
method: "ЭУГ-ЗЗЭУХ болон НУГ-АХ-ээс Var лимит зөрчсөн тоог авна."
period_text: "Сүүлийн 1 жилд"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
