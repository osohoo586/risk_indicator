/*---
indicator_id: RI_18_0676
name_mn: "Нийт идэвхтэй харилцагчийн тоо - ОН /Ритэйл/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ИБГ-БХ"
required_info: "Харилцагчийн мэдээлэл"
method: "ОН - Тухайн хугацаанд зээлтэй  эсвэл Хугацаатай хадгаламж байгаа эсвэл Эх үүсвэрийн аль нэг данс нь сүүлийн 3 сар тогтмол сард 3-с дээш гүйлгээ хийсэн эсвэл  Credit card -тай эсвэл Аккредетив, Баталгаа, лимит Аль 1 нь байгаа (Салбар дээрх R) (Primary SOL-р)"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
