/*---
indicator_id: RI_09_0337
name_mn: "Салбарын орлон ажиллах хүсэлтийг шийдвэрлэх"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-79% хүртэл
  4-80-84%
  3-85-90%
  2-90-94%
  1-95-100%
source_system: "СБМХ"
required_info: "Орлон ажиллах хүсэлтийн шийдвэрлэлт"
method: "Орлон ажиллах хүсэлтийг шийдвэрлэсэн байдлыг харгалзан үнэлнэ"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
