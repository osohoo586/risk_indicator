/*---
indicator_id: RI_28_1062
name_mn: "POS, POB-ын эвдрэл, гэмтэл"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.8                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-9% ба түүнээс дээш
  4-7%-9%
  3-4%-6%
  2-1%-3%
  1-Зөрчилгүй
source_system: "ДБГ-ЦХАХ"
required_info: "Эвдрэлтэй ПОС-ын мэдээлэл"
method: |
  Эвдрэлтэй ПОС/Нийт ПОС
  Ашиглах хугацаа дуусч актлагдсан тохиолдол тооцоололд оруулахгүй.
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
