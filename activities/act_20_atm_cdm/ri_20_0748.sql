/*---
indicator_id: RI_20_0748
name_mn: "АТМ,CDM түрээсийн гэрээний зөрчил"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-5% ба түүнээс дээш зөрчилтэй
  4-4-4.9% зөрчилтэй
  3-3-3.9% зөрчилтэй
  2-1-2.9% зөрчилтэй
  1-Зөрчилгүй
source_system: "ДБГ-ЦХАХ"
required_info: "Гэрээний жагсаалт"
method: "Гэрээний зөрчилтэй АТМ,CDM/Нийт түрээсийн гэрээтэй ATM"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
