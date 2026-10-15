/*---
indicator_id: RI_26_0971
name_mn: "Шимтгэл хураамжийн орлогын төлөвлөгөөний биелэлт - Дижитал бүтээгдэхүүн"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 2                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-90% ба түүнээс доош
  4-91%-93%
  3-94%-96%
  2-97%-99%
  1-100% ба түүнээс дээш
source_system: "ДБХ, СУГ метрик"
required_info: "Шимтгэлийн орлого"
method: "Төлөвлөгөөний гүйцэтгэлээр үнэлнэ"
period_text: "Идэвхтэй харилцагчийн тооны зах зээлд эзлэх хувь"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
