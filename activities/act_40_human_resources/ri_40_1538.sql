/*---
indicator_id: RI_40_1538
name_mn: "Эргэц удирдсан байдал"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-7%-аас доош
  2-7-15%
  3-15.1-17.9%
  5-18% түүнээс дээш
source_system: "ХНУГ"
required_info: "Эргэц удирдах чиглэлд хийгдсэн ажлууд"
method: |
  1-3 чадамжтай ажлаас гарсан ажилтны тоо / Нийт 1-3 чадамж өндөртэй ажилтны тоо
  /ХНУГ-с гарсан ажилтнууд болон ХНУГ-н нийт бодит ажилтныг хасаж цэвэршүүлж тооцно/
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
