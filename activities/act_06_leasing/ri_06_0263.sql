/*---
indicator_id: RI_06_0263
name_mn: "Санхүүгийн түрээсийн судалгааны чанар"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score4"
scale_text: |
  5-0-59%
  4-60-69%
  3-70-79%
  2-80-89%
  1-90-100%
source_system: "ЗГ-ЗМХ"
required_info: "ЗГ-ЗМХ-с хэрэгжүүлсэн хяналт хийсэн мэдээлэлд үндэслэн дүгнэнэ."
method: "ЗГ-аас харилцагчийн зээлийн судалгаа тус бүрт өгсөн үнэлгээний дунджаар тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
