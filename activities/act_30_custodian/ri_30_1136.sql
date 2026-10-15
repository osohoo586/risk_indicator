/*---
indicator_id: RI_30_1136
name_mn: "ҮЦЗЗ дээр ажиллах эрхийн хүчинтэй хугацаа"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-51-100% эрхийн хугацаа дууссан
  4-Эрхүүдийн 50% хүчинтэй
  3-Эрхүүдийн 60% хүчинтэй
  2-Эрхүүдийн 80% хүчинтэй
  1-Эрхүүд бүгд хүчинтэй
source_system: "Кастодиан банк"
required_info: "ҮЦЗЗ дээр ажиллах эрх"
method: "Нийт ажилтнуудын мэдээллийг авч эрхийн хүчинтэй хугацааг үзнэ"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
