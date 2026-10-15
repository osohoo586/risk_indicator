/*---
indicator_id: RI_01_0016
name_mn: "Нийт идэвхтэй харилцагчийн тоон төлөвлөгөөний биелэлт-Корпорэйт"
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
required_info: "Тухайн хугацаанд зээлтэй  эсвэл Хугацаатай хадгаламж байгаа эсвэл Эх үүсвэрийн аль нэг данс нь сүүлийн 3 сар тогтмол сард 3-с дээш гүйлгээ хийсэн эсвэл Credit card -тай эсвэл Аккредетив, Баталгаа, лимит Аль 1 нь байгаа/ BBG SOL R+C/ (Primary SOL-р)"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
# ── Тооцоолол ──
description: >
  Идэвхтэй корпорэйт харилцагч (primary SOL-оор) ÷ төлөвлөгөө. Идэвхтэй = тайлант сард зээл, хугацаатай
  хадгаламж, кредит карт, аккредитив / баталгаа / лимитийн аль нэг нь бий, ЭСВЭЛ сүүлийн 3 сар бүр ≥ 3 гүйлгээ.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH m3 AS (
    SELECT m.CIF_ID, COUNT(*) AS N_MONTHS
    FROM   {{schema.coremis}}.CUSTOMER_ACTIVITY_MONTHLY m
    WHERE  m.MONTH_END IN (:p_report_date, LAST_DAY(ADD_MONTHS(:p_report_date, -1)),
                           LAST_DAY(ADD_MONTHS(:p_report_date, -2)))
      AND  m.TXN_COUNT >= 3
    GROUP  BY m.CIF_ID
), act AS (
    SELECT c.PRIMARY_SOL_ID AS SOLID, COUNT(*) AS CNT
    FROM   {{schema.finacle}}.CMG c
    JOIN   {{schema.coremis}}.CUSTOMER_ACTIVITY_MONTHLY cur
           ON cur.CIF_ID = c.CIF_ID AND cur.MONTH_END = :p_report_date
    LEFT   JOIN m3 ON m3.CIF_ID = c.CIF_ID
    WHERE  c.SEGMENT = 'CORP'
      AND  (cur.HAS_LOAN = 'Y' OR cur.HAS_TD = 'Y' OR cur.HAS_CREDIT_CARD = 'Y' OR cur.HAS_LC_GUARANTEE = 'Y'
            OR NVL(m3.N_MONTHS, 0) = 3)
    GROUP  BY c.PRIMARY_SOL_ID
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(p.SOLID)                                             AS ENTITY_ID,
       NVL(a.CNT, 0)                                                AS NUMERATOR,      -- идэвхтэй
       p.ACTIVE_PLAN                                                AS DENOMINATOR,    -- төлөвлөгөө
       NVL(a.CNT, 0) / NULLIF(p.ACTIVE_PLAN, 0)                     AS VALUE
FROM   {{schema.coremis}}.CUSTOMER_PLAN p
LEFT   JOIN act a ON a.SOLID = p.SOLID
WHERE  p.TXNDATE = :p_report_date
  AND  p.SEGMENT = 'CORP'
