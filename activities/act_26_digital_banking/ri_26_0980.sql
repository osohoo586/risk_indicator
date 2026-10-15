/*---
indicator_id: RI_26_0980
name_mn: "Системийн тасралт/Нийт системийн ажилласан цаг"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-0.31%-аас их
  4-0.26-0.30%
  3-0.23-0.25%
  2-0.16-0.22%
  1-0.15%-аас бага
source_system: "МТАДАХ"
required_info: "МТАДАХ зайны аудитын үр дүн"
method: "Нийт системийн зогсолт нь нийт хугацааны хэдэн хувийг эзэлж байгааг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
