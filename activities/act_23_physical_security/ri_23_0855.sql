/*---
indicator_id: RI_23_0855
name_mn: "Дохиоллын компанийн шалгалтаар өгсөн зөвлөмжийн хэрэгжилт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Зөвлөмж хэрэгжүүлээгүй, 70%-аас бага.
  4-Зөвлөмжийн хэрэгжилт 70-79%
  3-Зөвлөмжийн хэрэгжилт 80-89%
  2-Зөвлөмжийн хэрэгжилт 90-99%
  1-Зөвлөмжийг бүрэн хэрэгжүүлсэн. /Зөвлөмжийн ирээгүй/
source_system: "АБХ"
required_info: "Дохиоллын компаны зөвлөмж"
method: "Дохиоллын компанаас өгсөн зөвлөмжийн хэрэгжилтийн мэдээг АБХ-ээс авч үнэлнэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
