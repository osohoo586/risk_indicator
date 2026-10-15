/*---
indicator_id: RI_01_0005
name_mn: "Алтны арилжааны ашиг - Корпорэйт - УУДБХ"
status: REVIEW
version: 0.1.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "BI тайлангийн систем"
required_info: "Орлого, үр дүнгийн тайлан /ББГ-ын харилцагчдын Голомт банканд тушаасан алтны арилжааны ашиг /GL -42200//"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
# ── Тооцоолол: RI_01_0004-ийн SQL (IN2003), зөвхөн алтны арилжааны ашгийн (GL 42200) мөрүүд ──
sql_from: SH_031
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
# p_pkeys: IN2003 тайлангийн алтны арилжааны ашгийн (GL 42200) мөрийн PKEY-ууд (таслалаар). Орчин бүрт config/<env>.yaml params-аар; "TODO" бол ажиллахгүй (PARAMS_TODO).
params: {p_pkeys: "TODO"}
source_check: |
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA
  WHERE REPORTNO = 'IN2003' AND TXNDATE = :p_report_date
max_change_pct: {pct: 30}
---*/
