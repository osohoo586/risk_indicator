/*---
indicator_id: RI_97_9003
name_mn: 100 харилцагчид ногдох банкны буруутай гомдол
name_en: Bank-fault complaints per 100 customers
description: >
  ТУРШИЛТ — тайлант улиралд ХҮГ-д бүртгэгдсэн банк, ажилтны буруутай гомдол ÷ (primary SOL-оор) харилцагч × 100.
  COREMIS (гомдол) + FINACLE (харилцагч) — хоёр schema-г нэг SQL-д.
status: IN_PROGRESS
version: 0.1.0
scale_text: |
  1-1-ээс бага
  2-1-2.9
  3-3-4.9
  4-5-9.9
  5-10 ба түүнээс дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH c AS (
    SELECT c.SOLID, COUNT(*) AS CNT
    FROM   {{schema.coremis}}.CUSTOMER_COMPLAINT c
    WHERE  c.CHANNEL = 'ХҮГ' AND c.IS_BANK_FAULT = 'Y'
      AND  c.REG_DATE >= :p_period_start
      AND  c.REG_DATE <  :p_report_date_next
    GROUP  BY c.SOLID
), k AS (
    SELECT m.PRIMARY_SOL_ID AS SOLID, COUNT(*) AS CNT
    FROM   {{schema.finacle}}.CMG m
    WHERE  m.REG_DATE <= :p_report_date
    GROUP  BY m.PRIMARY_SOL_ID
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(k.SOLID)                                             AS ENTITY_ID,
       100 * NVL(c.CNT, 0)                                          AS NUMERATOR,      -- гомдол × 100
       k.CNT                                                        AS DENOMINATOR,    -- харилцагч
       100 * NVL(c.CNT, 0) / k.CNT                                  AS VALUE
FROM   k
LEFT   JOIN c ON c.SOLID = k.SOLID

/* ═══ ClickHouse-д шалгах ══════════════════════════════════════════════════════════════════════
   Энэ comment-ийг runner ажиллуулахгүй. Доорх query-г ClickHouse дээр хуулж ажиллуулна:
   DBeaver «RA ClickHouse — үр дүн (local docker)» холболт, эсвэл http://localhost:8123/play
   (Query-г энэ файлд uncomment хийхгүй — тэгвэл Oracle дээр SQL-тэй хамт ажиллаж алдаа өгнө.)

   1) Run-ээс ӨМНӨ   (а) → status = БАЙХГҮЙ, rows = 0      (б) → хоосон
   2) Ажиллуулах     python ri.py run --env local activities/act_97_practice/ri_97_9003.sql -p 2026-Q3
   3) Run-ий ДАРАА   (а) → status = БАЙНА, rows = 1        (б) → салбарын сүлжээний (1500) утга, оноо, SOLID-ууд
                     (в) SOL бүрийн задаргаа ri_result-д хадгалагдахгүй: run … --save-csv → output/local/ri_97_9003_20260930.csv
                     Дахин run хийвэл rows хэвээр (хуучин мөр ri_history-д шилжинэ — давхардахгүй)
   4) Тулгах         python ri.py verify --env local activities/act_97_practice/ri_97_9003.sql -p 2026-Q3

-- (а) ri_result-д орсон эсэх
SELECT if(count() = 0, 'БАЙХГҮЙ', 'БАЙНА') AS status, count() AS rows
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9003' AND snapshot_date = '2026-09-30';

-- (б) Үйл ажиллагааны (BRANCHID 1500) утга, оноо, SOLID-ууд
SELECT activity, activity_id, solid, branch_id, risk_indicator, risk_ind_id, result_number, result,
       snapshot_date, run_id, loaded_at
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9003' AND snapshot_date = '2026-09-30';
═════════════════════════════════════════════════════════════════════════════════════════════════ */
