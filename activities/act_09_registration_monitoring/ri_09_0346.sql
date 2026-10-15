/*---
indicator_id: RI_09_0346
name_mn: "Монголбанкны үүргийн биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Биелэлт хангалтгүй
  0-Биелэлт тооцох болоогүй
source_system: "АХЗ-ээс мэдээлэл авах. СУГ"
required_info: "Үүргийн биелэлт"
method: "Монголбанкны үүргийн биелэлтэд үндэслэн үнэлнэ"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
