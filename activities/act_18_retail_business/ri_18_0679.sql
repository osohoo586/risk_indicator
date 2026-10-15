/*---
indicator_id: RI_18_0679
name_mn: "Нийт идэвхитэй харилцагчийн тоо - Дижитал суваг - ОН"
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
required_info: |
  Зээлийн мэдээлэл
  Кредит картын мэдээлэл
method: "ОН- Сард 3 болон түүнээс дээш гүйлгээ хийсэн OR Сард 2 болон түүнээс дээш логин хийсэн харилцагч (Зөвхөн retail харилцагчид )"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
