/*---
indicator_id: RI_32_1229
name_mn: "Facebook, twitter, instagram дагагчийн тоогоор банкны системийн"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  0-Гэрээний үүрэг зөрчигдөөгүй
  3-Гэрээний үүрэг зөрчигдсөн боловч банк хохироогүй
  5-Гэрээний үүрэг зөрчигдөж банк хохирсон
source_system: "МХ"
required_info: "Гэрээний үүрэг зөрчсөн байгууллагын тоо"
method: "Хамтран ажилладаг байгууллагууд гэрээний үүргээ зөрчсөн эсэхийг харгалзан үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
