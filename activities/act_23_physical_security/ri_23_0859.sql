/*---
indicator_id: RI_23_0859
name_mn: "Банкны байр, салбар тооцооны төв, АТМ, СДМ-д гадны этгээд халдаж банкинд биет хохирол гаргах, мөнгө дээрэмдүүлсэн эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Халдлага гарсан
  3-Халдлагын сэжигтэй тохиолдол бүртгэгдсэн
  0-Халдлага гараагүй
source_system: "АБХ"
required_info: "Халдлагын мэдээлэл"
method: "Халдлагын тохиолдол бүртгэгдсэн эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
