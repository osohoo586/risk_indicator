/*---
indicator_id: RI_34_1295
name_mn: "Төслийн эрсдэл, чанарын хэмжүүрийг тодорхойлсон эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Эрсдэл, Чанарын хэмжүүр тодорхойгүй
  1-Эрсдэл, Чанарын хэмжүүр тодорхой
source_system: "ДШГ-ТУХ"
required_info: "Эрсдэлийн чанарын хэмжүүр"
method: "Төсөл эхлэхэд заавал тодорхойлсон байх ёстой эрсдэл, чанарын үнэлгээний хэмжүүрийг тодорхойлсон эсэхийг үзэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
