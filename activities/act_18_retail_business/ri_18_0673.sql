/*---
indicator_id: RI_18_0673
name_mn: "Нийт ритэйл харилцагчийн тоо - УБ"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ИБГ-БХ"
required_info: "Харилцагчийн мэдээлэл"
method: "Зээлтэй/Харилцахтай/Хадгаламжтай харилцагчдаас ББГ-д бүртгэлтэйгээс бусад R ээр эхэлсэн CIF тоо (Primary SOL-р)"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
