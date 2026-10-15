/*---
indicator_id: RI_11_0414
name_mn: "Чанаргүй зээлийн харьцаа (NPL ratio) - ГХС"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-2.2% ба түүнээс бага
  2-2.2%-2.4%
  3-2.5%-2.9%
  4-3.0%-4.9%
  5-5% ба түүнээс дээш
source_system: "ХБСХ"
required_info: "Чанаргүй зээлийн мэдээ"
method: "Чанаргүй зээл/Нийт зээл"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
