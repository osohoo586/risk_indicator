/*---
indicator_id: RI_97_9006
name_mn: Хүний нөөц ба зээлийн нийлмэл эрсдэл
name_en: Combined staff and credit risk
description: >
  ТУРШИЛТ — өөр үзүүлэлтийн ҮР ДҮНГЭЭС тооцох жишээ (dependencies). RI_97_9001 (туршлага багатай ажилтан) ба
  RI_97_9004 (хугацаа хэтэрсэн зээл)-ийн үйл ажиллагааны утгын (result_number) дундаж — ClickHouse-ийн ri_result-аас
  ЗӨВХӨН уншина.
  Runner эхлээд dependency-г, дараа нь үүнийг ажиллуулна; dependency амжилтгүй бол SKIPPED (DEPENDENCY_FAILED).
connection: clickhouse_ra
dependencies: [RI_97_9001, RI_97_9004]
status: IN_PROGRESS
version: 0.1.0
scale_text: |
  1-10%-аас бага
  2-10%-19.9%
  3-20%-29.9%
  4-30% ба түүнээс дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                AS ENTITY_LEVEL,
       r.branch_id                               AS ENTITY_ID,
       sum(r.result_number)                      AS NUMERATOR,      -- хоёр үзүүлэлтийн утгын нийлбэр
       count()                                   AS DENOMINATOR,    -- үзүүлэлтийн тоо
       sum(r.result_number) / count()            AS VALUE
FROM   {{schema.ri}}.ri_result r
WHERE  r.risk_ind_id IN ('RI_97_9001', 'RI_97_9004')
  AND  r.snapshot_date = {p_report_date:Date}
  AND  r.result_number IS NOT NULL
GROUP  BY r.branch_id
