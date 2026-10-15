/*---
indicator_id: RI_40_1533
name_mn: "Банкны 1 ажилтанд ногдох сургалт цаг"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-16 цагаас дээш
  2-14-15.9 цаг
  3-12-13.9 цаг
  4-10-11.9 цаг
  5-10 доош цаг
source_system: "ХНУГ-ҮАХ-СХА"
required_info: "Сургалт цаг"
method: "Нийт сургалтын цаг/Ажилтны тоо"
period_text: "Сүүлийн 1 жил"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
