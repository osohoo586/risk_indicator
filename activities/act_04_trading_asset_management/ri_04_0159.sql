/*---
indicator_id: RI_04_0159
name_mn: "Своп хэлцлийг амжилттай хаах"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Үнэлэхгүй /Тухайн хугацаанд хэлцэл хийгдээгүй/
  1-Тийм
  5-Үгүй
source_system: "Своп хэлцлийг амжилттай хаасан байдлаар тооцох"
required_info: "Нэгжээс ирүүлсэн мэдээлэл"
method: "Своп хэлцлийг амжилттай хаасан байдлаар тооцно."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
