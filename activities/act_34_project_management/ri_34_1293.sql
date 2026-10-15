/*---
indicator_id: RI_34_1293
name_mn: "Хугацаа хэтрэх\nХугацаандаа хаагдсан амжилттай төслийн хувь"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Хугацаа хэтрүүлсэн төсөл байгаа
  1-Хугацаа хэтрүүлсэн төсөл байхгүй
source_system: "ДШГ-ТУХ"
required_info: "Төслийн хугацаа хэтрэлт"
method: "Төслийн хугацаа хэтрэлтийг харгалзан үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
