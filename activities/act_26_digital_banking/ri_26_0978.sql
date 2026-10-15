/*---
indicator_id: RI_26_0978
name_mn: "Дижитал бүтээгдэхүүний нөхцөл, үйлчилгээний процесс нь хууль эрх зүйн заалтыг зөрчсөн тохиолдол гарсан эсэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Тийм
  0-Үгүй
source_system: "ДАГ-гомдлын бүртгэл, ХҮГ-ийн бүртгэл"
required_info: "ДАГ-гомдлын бүртгэл, ХҮГ-ийн бүртгэл"
method: "Банкинд ирсэн болон ДАГ-т ирсэн гомдлын бүртгэлээр үнэлнэ /ибанк, смарт банк, сошэйлпэй, киоск, мобайл банк/"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
