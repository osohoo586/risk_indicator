/*---
indicator_id: SH_009
name_mn: "Нийт ногоон зээлийн төлөвлөгөөний биелэлт"
description: >
  Ногоон зээлийн үлдэгдэл (FINACLE, LAM.IS_GREEN = Y) ÷ төлөвлөгөө (COREMIS.GREEN_LOAN_PLAN), тайлант өдрөөр.
  Төлөвлөгөөтэй SOL л орно. VALUE = харьцаа (0.95 = 95%).
  Ашигладаг: RI_01_0006, RI_02_0054, RI_06_0224
connection: oracle_whouse
frequency: quarterly
period: report                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 3 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
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
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH g AS (
    SELECT b.SOL_ID, SUM(b.OUTSTANDING_AMT) AS AMT, COUNT(*) AS CNT
    FROM   {{shared.finacle.loan_book}} b
    WHERE  b.IS_GREEN = 'Y'
    GROUP  BY b.SOL_ID
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(p.SOLID)                              AS ENTITY_ID,
       NVL(g.AMT, 0)                                 AS NUMERATOR,      -- гүйцэтгэл
       p.PLAN_AMT                                    AS DENOMINATOR,    -- төлөвлөгөө
       NVL(g.AMT, 0) / NULLIF(p.PLAN_AMT, 0)         AS VALUE,
       NVL(g.CNT, 0)                                 AS SOURCE_ROW_COUNT
FROM   {{schema.coremis}}.GREEN_LOAN_PLAN p
LEFT   JOIN g ON g.SOL_ID = p.SOLID
WHERE  p.TXNDATE = :p_report_date
