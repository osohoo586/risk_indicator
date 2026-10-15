/*---
indicator_id: RI_28_1065
name_mn: "КҮБ, И-КҮБ болох хүсэлтийг шийдвэрлэсэн дундаж хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Ажлын 9-аас дээш хоногт
  4-Ажлын 9 хоногт
  3-Ажлын 8 хоногт
  2-Ажлын 7 хоногт
  1-Ажлын 6 хоногт
source_system: "JIRA"
required_info: "Жира, КҮБ-шинэ хүсэлт"
method: "Хүсэлт хүлээн авсанаас POS суурилуулах хүртэлх хугацааг ажлын хоногоор хэмжиж үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
