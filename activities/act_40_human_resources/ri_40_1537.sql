/*---
indicator_id: RI_40_1537
name_mn: "Ажилтны ур чадварын түвшин"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-95.1% ба түүнээс дээш
  2-90%-95%
  3-85%-89%
  4-80%-85%
  5-80%-с доош
source_system: "ХНУГ"
required_info: "Ажилтнуудын ур чадварын үнэлгээний дундаж"
method: |
  Нийт ажилтны ур чадварын үнэлгээ 60%-с доош үнэлэгдсэн ажилтны хувь
  Энэ үзүүлэлт зөвхөн 2-р хагас жилд үнэлэгдэнэ.
  /зорилтот түвшнээс бага үнэлэгдсэн ажилтны хувийг 10%-с бага түвшинд барьж ажиллах/
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
