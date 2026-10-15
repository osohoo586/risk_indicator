/*---
indicator_id: RI_26_0983
name_mn: "Нийт харилцагч байгууллагын тоо - Лояалти"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Өмнөх улирлаас өссөн. Зорилтод хүрсэн
  2-Өмнөх улирлаас буурсан. Зорилтод хүрсэн
  3-Өмнөх улирлаас өссөн. Зорилтод хүрээгүй
  5-Өмнөх улирлаас буурсан. Зорилтод хүрээгүй
source_system: "ДБХ"
required_info: "Байгууллагын жагсаалт"
method: "Төлөвлөгөөний гүйцэтгэлээр үнэлнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
