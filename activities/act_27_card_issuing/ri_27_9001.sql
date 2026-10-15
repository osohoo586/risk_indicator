/*---
indicator_id: RI_27_9001
name_mn: "Картын залилангийн гүйлгээний хувь (DEMO, ClickHouse source)"
name_en: Card fraud transaction ratio
description: >
  Master-т байхгүй НЭМЭЛТ үзүүлэлт (9001+, жингүй — нийт оноонд орохгүй): ClickHouse source-ийн жишээ.
  Үйл ажиллагааны SOL-уудын гаргасан картын гүйлгээнээс залилан гэж баталгаажсан (is_fraud = 1)-ын хувь,
  тайлант хугацаанд. cardzone_dwh.card_txn = CARDZONE.CARD_TXN-ийн DWH хуулбар (картыг гаргасан SOL-той).
connection: clickhouse_dwh
frequency: quarterly
status: REVIEW
version: 1.0.0
scale_text: |
  1-0.5%-аас бага
  2-0.5%-1%
  3-1%-2%
  4-2%-3%
  5-3%-аас дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                     AS ENTITY_LEVEL,
       toString(t.issue_sol_id)                  AS ENTITY_ID,
       countIf(t.is_fraud = 1)                   AS NUMERATOR,      -- залилан
       count()                                   AS DENOMINATOR,    -- нийт гүйлгээ
       countIf(t.is_fraud = 1) / count()         AS VALUE,
       count()                                   AS SOURCE_ROW_COUNT
FROM   {{schema.cardzone_dwh}}.card_txn t
WHERE  t.txn_date >= {p_period_start:Date}
  AND  t.txn_date <= {p_report_date:Date}
GROUP  BY t.issue_sol_id
