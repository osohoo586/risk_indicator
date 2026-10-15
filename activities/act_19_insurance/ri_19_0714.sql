/*---
indicator_id: RI_19_0714
name_mn: "Шимтгэлийн орлого/БЗ-н даатгал+бусад/"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  84% ба түүнээс доош-Тийм
  85%-89%-
  90%-94%-
  95%-99%-
  100% ба түүнээс дээш-
source_system: "BI"
required_info: "Орлого үр дүнгийн тайлан"
method: "Нийт даатгагдах БЗ-н шимтгэлийн орлогын төлөвлөгөө, гүйцэтгэл."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
