/*---
indicator_id: RI_02_0090
name_mn: "Харилцагчийн сэтгэл ханамжийн индекс - SME"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score4"
scale_text: |
  1-Зорилтод түвшинд хүрсэн.
  5-Зорилтод түвшинд хүрээгүй.
source_system: "МХ"
required_info: "Судалгааны үр дүн"
method: "МОНХГ-СХА-с хагас жил тутам харилцагчдаас авдаг сэтгэл ханамжийн судалгааны үнэлгээгээр тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
