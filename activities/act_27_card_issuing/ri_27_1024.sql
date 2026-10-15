/*---
indicator_id: RI_27_1024
name_mn: "Сэжигтэй гүйлгээний илэрц тоо хэмжээ өсөх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Өмнөх үеэс өссөн
  1-Өмнөх үеэс буурсан
source_system: "ДБГ-КХ-КЭУА"
required_info: "Сэжигтэй гүйлгээ, chargeback-ийн тайлан"
method: "Аудит орсноос хойш улирлын дундаж нь аудит орох үеийн илэрцээс өссөн эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
