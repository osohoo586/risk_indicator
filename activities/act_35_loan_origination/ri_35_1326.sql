/*---
indicator_id: RI_35_1326
name_mn: "Зээлийн хороодын дарга, гишүүд солигдсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.39                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Дарга солигдсон
  3-Гишүүд солигдсон
  1-Дарга, гишүүд өөрчлөгдөөгүй
source_system: "ЗГ"
required_info: "Хороодын гишүүд, дарга нар"
method: "Хороодын нарийн бичгээс тодруулж үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
