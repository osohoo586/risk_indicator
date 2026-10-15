/*---
indicator_id: RI_34_1292
name_mn: "Зардал хэтрэх, Төслүүдийн зардлын гүйцэтгэл"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зардал хэтрүүлсэн төсөл байгаа
  1-Зардал хэтрүүлсэн төсөл байхгүй
source_system: "ДШГ-ТУХ"
required_info: "Төслийн зардлын гүйцэтгэл"
method: "Төслийн зардлын гүйцэтгэлийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
