/*---
indicator_id: RI_16_0597
name_mn: "Ложистикийн тээврийн хэрэгсэл тодорхойлсон маршрут зөрчсөн тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Маршрут хянадаггүй эсвэл хэрэгжилт 85%-аас доош, батлагдаагүй байх
  4-Хэрэгжилт 85-89%
  3-Хэрэгжилт 90-94%
  2-Хэрэгжилт 95-99%
  1-Хэрэгжилт 100%
source_system: "ХБГ-АЛА"
required_info: "Ложистикийн бүртгэл"
method: "Маршрут зөрчсөн тохиолдол гарсан эсэхийг харгалзан үнэлнэ."
period_text: "Аудит орсноос хойш улирлын дундаж"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
