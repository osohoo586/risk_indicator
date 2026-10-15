/*---
indicator_id: RI_01_0015
name_mn: "Дижитал идэвхтэй харилцагчийн тоон төлөвлөгөөний биелэлт - Корпорэйт"
status: REVIEW
version: 1.0.0
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
required_info: "Сард 3 болон түүнээс дээш гүйлгээ хийсэн + Сард 2 болон түүнээс дээш логин хийсэн харилцагч - SOL811, 812, 814"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
# ── Тооцоолол ──
description: >
  Дижитал идэвхтэй корпорэйт харилцагч (тайлант сард ≥ 3 гүйлгээ БА ≥ 2 цахим нэвтрэлт, primary SOL-оор)
  ÷ төлөвлөгөө (COREMIS.CUSTOMER_PLAN.DIGITAL_ACTIVE_PLAN — мастерийн дагуу SOL 811, 812, 814-т л байна).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH act AS (
    SELECT c.PRIMARY_SOL_ID AS SOLID, COUNT(*) AS CNT
    FROM   {{schema.coremis}}.CUSTOMER_ACTIVITY_MONTHLY m
    JOIN   {{schema.finacle}}.CMG c ON c.CIF_ID = m.CIF_ID
    WHERE  m.MONTH_END = :p_report_date
      AND  c.SEGMENT = 'CORP'
      AND  m.TXN_COUNT >= 3
      AND  m.LOGIN_COUNT >= 2
    GROUP  BY c.PRIMARY_SOL_ID
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(p.SOLID)                                             AS ENTITY_ID,
       NVL(a.CNT, 0)                                                AS NUMERATOR,      -- дижитал идэвхтэй
       p.DIGITAL_ACTIVE_PLAN                                        AS DENOMINATOR,    -- төлөвлөгөө
       NVL(a.CNT, 0) / NULLIF(p.DIGITAL_ACTIVE_PLAN, 0)             AS VALUE
FROM   {{schema.coremis}}.CUSTOMER_PLAN p
LEFT   JOIN act a ON a.SOLID = p.SOLID
WHERE  p.TXNDATE = :p_report_date
  AND  p.SEGMENT = 'CORP'
  AND  p.DIGITAL_ACTIVE_PLAN IS NOT NULL
