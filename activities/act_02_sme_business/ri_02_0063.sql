/*---
indicator_id: RI_02_0063
name_mn: "Зээлийн эргэн хяналт хийгдсэн зээлийн хувь - SME"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-0-59%
  4-60-69%
  3-70-79%
  2-80-89%
  1-90-100%
source_system: "ЗГ-ЗМХ"
required_info: "Өр цуглуулах, эргэн хяналт, ЗХБ, зээлийн материал буцаалтын үйл ажиллагааны тайлан"
method: "Зээлийн эргэн хяналтын чанарыг аудит орсноос хойшхи бүх улирлын дундаж үнэлгээгээр үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
