/*---
indicator_id: RI_20_0753
name_mn: "АТМ-н тасралтгүй ажиллагаа - БТГ-АТМ алба"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Нийт гүйлгээний 0.1%-с хэтэрсэн.
  4-Нийт гүйлгээний 0.08-0.099%
  3-Нийт гүйлгээний 0.06-0.079%
  2-Нийт гүйлгээний 0.04-0.059%
  1-Нийт гүйлгээний 0.04%-аас бага
source_system: "БТГ-ДТТХ"
required_info: "Хяналтын тайлан мэдээлэл"
method: "Тухайн нэгжээс хамааран тасарсан АТМ-д харгалзах оноог авах ёстой онооноос хасаж тухайн нэгжийн авах оноог гаргана"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
