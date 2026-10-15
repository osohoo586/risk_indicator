/*---
indicator_id: RI_28_1064
name_mn: "КҮБ-д үзүүлэх засварын үйлчилгээг гүйцэтгэсэн хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Ажлын 5-аас дээш хоногт
  4-Ажлын 5 хоногт
  3-Ажлын 4 хоногт
  2-Ажлын 3 хоногт
  1-Ажлын 1-2 хоногт
source_system: "JIRA"
required_info: "Жира, дуудлага үйлчилгээ"
method: "Дуудлага хүлээн авсанаас шийдвэрлэсэн хүртэлх хугацааг ажлын хоногоор хэмжиж үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
