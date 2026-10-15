/*---
indicator_id: RI_16_0589
name_mn: "Хугацаандаа баримт, тайлангаа хүргүүлээгүй салбарын тоо өсөх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-79% хүртэл
  2-80-84%
  3-85-90%
  4-90-94%
  5-95-100%
source_system: "ХБХХ"
required_info: "Өдрийн гүйлгээний баримт, хувийн хэргийг хүргүүлсэн мэдээлэл"
method: "Заагдсан хугацаанд тайлангаа ирүүлээгүй салбарын тоо/(ажлын хоног*Нийт салбар)"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
