/*---
indicator_id: RI_22_0825
name_mn: "Банкны хөрөнгө оруулагчидад зориулсан эвэнт арга хэмжээ зохион байгуулсан байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-96%-аас дээш
  3-90% - 95.9%
  5-90% - с доош
source_system: "ХОХХ"
required_info: "ХОХХ-с хөрөнгө оруулагчдад зориулсан арга хэмжээ зохион байгуулж ажилласан байдал"
method: "Хамрах хугацаанд төлөвлөсөн ажлын гүйцэтгэлд үндэслэн тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
