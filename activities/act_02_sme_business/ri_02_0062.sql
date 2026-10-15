/*---
indicator_id: RI_02_0062
name_mn: "Төслийн дансны тооцоо нийлэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Зөрүүтэй тайлагнасан тохиолдол гараагүй.
  5-Зөрүүтэй тайлагнасан тохиолдол гарсан.
source_system: "ЖДБГ-БХХ"
required_info: "Нэгжээс ирүүлсэн мэдээлэл"
method: "Тооцоо зөрсөн тохиолдол гарсан эсэх, хөндлөнгийн байгууллагаас акт, зөрчил ирсэн эсэх,"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
