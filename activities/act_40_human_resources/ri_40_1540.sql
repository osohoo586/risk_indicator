/*---
indicator_id: RI_40_1540
name_mn: "Ротацийн төлөвлөгөөний биелэлт"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-Төлөвлөгөө биелсэн
  5-Төлөвлөгөө биелээгүй
source_system: "ХНУГ"
required_info: "Төлөвлөгөө, биелэлт"
method: |
  Төлөвлөгөөний дагуу тухайн хугацаанд ротацид орсон ажилтны хувь
  Дараах нөхцлүүдийг цэвэршүүлж тооцно.
  - Ажлаас гарсан
  - Жирэмсний амралт,чөлөө
  - Сэлгэх боломжгүй
  - Нэгжийн удирдлагаас сэлгэхгүй гэсэн
  - СШ-т ороод тэнцээгүй
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
