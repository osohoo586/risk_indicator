/*---
indicator_id: RI_20_0751
name_mn: "Монгол улсад ATM - ийн төхөөрөмжид луйврын гүйлгээ гарсан эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Луйвар гарсан
  0-Луйвар гараагүй
source_system: "Монгол банкны site"
required_info: "Төлбөрийн системийн тайлан"
method: "Залилангийн гүйлгээний мэдээ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
