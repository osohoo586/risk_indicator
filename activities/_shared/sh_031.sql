/*---
indicator_id: SH_031
name_mn: "Дотоод үнэлгээний ашгийн төлөвлөгөөний биелэлт"
status: REVIEW
version: 0.1.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "BI тайлангийн систем"
required_info: "Орлого, үр дүнгийн тайлан"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
connection: oracle_whouse
description: >
  Орлогын төлөвлөгөөний (BI тайлан IN2003) биелэлт = Σ гүйцэтгэл (BALANCE) / Σ өссөн дүнгийн
  төлөвлөгөө (RUNNING_BUDGET), SOL бүрээр. Хуучин load_fni1041 (RISKASSESSMENT.FNI1041)-ээс:
  1) Хуучин нь бүх мөрийг (хасах жагсаалтаас бусад) PKEY-ээр хадгалдаг байсан; энд p_pkeys-ээр
     тухайн үзүүлэлтийн мөрүүдийг сонгоно (заавал — хоосон бол 0 мөр).
  2) Төлөвлөгөө 0 үед хуучин нь 100% гэж үздэг байсан; энд VALUE NULL (оноонд Үнэлэхгүй).
  3) 100%-иар таслахгүй (LEAST(...,1) хассан) — шатлалд нөлөөгүй.
  4) Огноо зөвхөн тайлант өдөр (хуучин нь ±4 хоног хайдаг).
  ЭХ SQL: RI_01_0005, RI_01_0008, RI_01_0014 нь sql_from-оор ашиглана.
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
# p_pkeys: дотоод үнэлгээний ашгийн мөрийн PKEY-ууд. Орчин бүрт config/<env>.yaml params-аар.
params: {p_pkeys: "TODO"}
source_check: |
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA
  WHERE REPORTNO = 'IN2003' AND TXNDATE = :p_report_date
max_change_pct: {pct: 30}
---*/
SELECT 'SOL'                                                 AS ENTITY_LEVEL,
       TO_CHAR(s.SOL_ID)                                     AS ENTITY_ID,
       s.SOL_DESC                                            AS ENTITY_NAME,
       SUM(g.BALANCE)                                        AS NUMERATOR,     -- гүйцэтгэл
       SUM(g.RUNNING_BUDGET)                                 AS DENOMINATOR,   -- өссөн дүнгийн төлөвлөгөө
       SUM(g.BALANCE) / NULLIF(SUM(g.RUNNING_BUDGET), 0)     AS VALUE,
       COUNT(*)                                              AS SOURCE_ROW_COUNT
FROM   {{schema.coremis}}.GL_REPORT_DATA g
JOIN   {{schema.finacle}}.SOL s
       ON s.SOL_ID = g.BRANCH
WHERE  g.REPORTNO = 'IN2003'
  AND  g.VERSION  = '1'
  AND  g.TXNDATE  = :p_report_date
  AND  INSTR(',' || :p_pkeys || ',', ',' || g.PKEY || ',') > 0
GROUP  BY s.SOL_ID, s.SOL_DESC
