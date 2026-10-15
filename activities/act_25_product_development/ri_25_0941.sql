/*---
indicator_id: RI_25_0941
name_mn: "Депозит дансны хүүний зөрүү үүссэн эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 0.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөрүү гарсан
  0-Зөрүү гараагүй
source_system: "СУГ-ББХХ, ДАГ-ЗАЧБХ"
required_info: "Депозит дансны хүүний зөрүү үүссэх эсэх мэдээлэл"
method: "ДАГ-ын аудитаар бүтээгдэхнүүний нөхцөлтэй холбоотой зөрүү үүссэн эсэхийг харгалзан үнэлнэ. МТАДАХ, ЗАЧБХ, ЕАХ-ийн аудитын үр дүнгийн мэдээлэлд үндэслэнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
