/*---
indicator_id: RI_25_0938
name_mn: "Бүтээгдэхүүн үйлчилгээнд Portfolio анализ хийгддэг эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Тогтмол хийгддэг
  3-Шаардлагатай тохиолдолдолд хийдэг
  5-Бүх бүтээгдэхүүнд portfolio анализ хийгддэггүй
source_system: "ИБГ-ИБХХ"
required_info: "Хийгдсэн анализ, хяналт"
method: "Бүтээгдэхүүн хөгжлийн гарын авлагын дагуу бүтээгдэхүүнд portfolio анализ хийж байгаа эсэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
