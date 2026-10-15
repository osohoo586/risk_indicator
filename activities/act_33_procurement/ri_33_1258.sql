/*---
indicator_id: RI_33_1258
name_mn: "Төсөв хэтрүүлж хийгдсэн худалдан авалт байгаа эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 3                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Төсөв хэтрүүлж худалдан авалт хийгээгүй
  3-Батлагдсан худалдан авалтын төсөв хэтэрсэн боловч нөөц төсөвт багтсан.
  5-Батлагдсан худалдан авалтын төсөв хэтэрч нөөц төсвөөс нэмж зарцуулсан хэдий ч нөөц төсөв хэтэрсэн.
source_system: "СААХ"
required_info: "Худалдан авалтын мэдээ"
method: "Төсөв хэтрүүлсэн худалдан авалт хийгдсэн эсэх"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
