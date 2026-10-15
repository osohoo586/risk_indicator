/*---
indicator_id: RI_26_0972
name_mn: "Дижитал сувгаар хийсэн гүйлгээний тоон төлөвлөгөөний биелэлт /и-банк, смарт банк, сошэйлпэй, киоск, мобайл банк /"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
  0-Төлөвлөгөө өгөгдөөгүй /Үнэлэхгүй/
source_system: "ДБГ-ДБХ, СУГ метрик"
required_info: "Дижитал сувгийн гүйлгээний мэдээлэл"
method: "Төлөвлөгөөний гүйцэтгэлээр үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
