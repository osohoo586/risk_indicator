/*---
indicator_id: SH_032
name_mn: "Лизингийн багцын төлөвлөгөөни биелэлт"
status: REVIEW
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "BI тайлангийн систем"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
connection: oracle_whouse
sql_from: SH_029
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
# p_pkeys: GL3003a тайлангийн лизингийн багцын мөрийн PKEY-ууд (таслалаар). Орчин бүрт config/<env>.yaml params-аар; "TODO" бол ажиллахгүй (PARAMS_TODO).
params: {p_pkeys: "TODO"}
source_check: |
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA
  WHERE REPORTNO = 'GL3003a' AND TXNDATE = :p_report_date
max_change_pct: {pct: 30}
---*/
