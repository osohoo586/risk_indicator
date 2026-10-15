/*---
indicator_id: RI_25_0940
name_mn: "КҮБ-н шимтгэлийн орлого - retial"
manual: true                    # хүн үнэлнэ: ri.py manual template / load
status: TODO
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
source_system: "BI тайлангийн систем"
required_info: "ББГ-д бүртгэлтэй КҮБ-н шимтгэлийн орлого, E-commerce, SocialPay Instore үйлчилгээний шимтгэлийн орлогууд"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
---*/
