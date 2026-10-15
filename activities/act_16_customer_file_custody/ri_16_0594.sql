/*---
indicator_id: RI_16_0594
name_mn: "Ложистикийн үйл ажиллагааг зохицуулсан журамгүй байх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Ложистикийн үйл ажиллагааг зохицуулсан журам, заавар батлагдсан
  3-Журам, заавар боловсруулагдаж байгаа
  5-Зохицуулсан журам зохицуулалтгүй
source_system: "ХБГ-АЛА"
required_info: "Ложистикийн үйл ажиллагааг зохицуулсан журам"
method: "Зохицуулсан журам батлагдсан эсэхийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
