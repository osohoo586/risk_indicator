/*---
indicator_id: RI_30_1143
name_mn: "Зохицуулагч байгууллагад хүргүүлдэг тайланг хоцроосон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хоцроосон тохиолдол гарсан
  0-Хоцроосон тохиолдол гараагүй
source_system: "Кастодиан банк"
required_info: "Зохицуулагч байгууллагуудад хүргүүлсэн тайлан"
method: "Сар бүр СЗХ-д, улирал бүрд МБ-д хүргүүлдэг тайланг хоцроосон тохиолдол гарсан эсэх"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
