/*---
indicator_id: RI_01_0014
name_mn: "КҮБ-н шимтгэлийн орлого - Корпорейт"
status: REVIEW
version: 0.1.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
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
automatable: "Тийм"
# ── Тооцоолол: RI_01_0004-ийн SQL (IN2003), зөвхөн КҮБ-ийн шимтгэлийн орлогын (E-commerce, SocialPay Instore) мөрүүд ──
sql_from: SH_031
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
# p_pkeys: IN2003 тайлангийн КҮБ-ийн шимтгэлийн орлогын (E-commerce, SocialPay Instore) мөрийн PKEY-ууд (таслалаар). Орчин бүрт config/<env>.yaml params-аар; "TODO" бол ажиллахгүй (PARAMS_TODO).
params: {p_pkeys: "TODO"}
source_check: |
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA
  WHERE REPORTNO = 'IN2003' AND TXNDATE = :p_report_date
max_change_pct: {pct: 30}
---*/
