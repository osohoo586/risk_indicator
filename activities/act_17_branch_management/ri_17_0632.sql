/*---
indicator_id: RI_17_0632
name_mn: "Биет сувгийн хөрөнгө оруулалтыг заасан хугацаанд нөхсөн эсэх."
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-31% ба түүнээс дээш нөхөөгүй
  4-21%-30% нөхөөгүй
  3-11%-20% нөхөөгүй
  2-1%-10% нөхөөгүй
  1-Бүрэн нөхсөн
source_system: "ИБГ-СУХ"
required_info: "Хөрөнгө оруулалтаа нөхөөгүй салбарын жагсаалт"
method: "Хөрөнгө оруулалтаа нөхөөгүй салбарын тоо/Нийт салбарын тоо"
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
