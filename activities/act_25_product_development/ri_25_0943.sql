/*---
indicator_id: RI_25_0943
name_mn: "Өөрчлөлтийн логийн түүврийн баталгаажуулалтаар зөрүү гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрүү гарсан
  0-Зөрүү гараагүй
source_system: "ДАГ"
required_info: "Хамрах хугацаанд аудитын баталгаажуулалттай холбоотой зөрүү гарсан эсэх, Гомдол баталгаажуулалт, Баталгаажуулах аудит."
method: "Хамрах хугацааны баталгаажуулалтын үр дүнд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
