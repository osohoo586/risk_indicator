/*---
indicator_id: RI_21_0787
name_mn: "Тодорхойлсон процессуудын үр ашгийг тооцдог эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Бүх процессын үр ашгийг тооцсон
  3-Зарим процессын үр ашгийг тооцсон
  5-Үр ашиг тооцоогүй
source_system: "БПМГ-ПУХ, СУГ"
required_info: "Үр ашгийн тооцоолол хийсэн мэдээлэл"
method: "Үр ашиг тооцсон процессын хувь хэмжээгээр тооцно"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
