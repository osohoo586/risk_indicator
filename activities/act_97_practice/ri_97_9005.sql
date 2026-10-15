/*---
indicator_id: RI_97_9005
name_mn: Терминалын залилангийн гүйлгээний хувь
name_en: Terminal fraud transaction share
description: >
  ТУРШИЛТ — тайлант улиралд салбарын ATM / POS терминалаар хийгдсэн гүйлгээнээс залилан гэж баталгаажсан хувь
  (Oracle CARDZONE.TERMINAL → терминалыг хариуцсан SOL). RI_27_9001 нь ClickHouse-оос, картыг гаргасан SOL-оор.
status: IN_PROGRESS
version: 0.1.0
scale_text: |
  1-0.5%-аас бага
  2-0.5%-1%
  3-1%-2%
  4-2%-3%
  5-3%-аас дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(t.SOL_ID)                                            AS ENTITY_ID,
       SUM(CASE WHEN x.IS_FRAUD = 'Y' THEN 1 ELSE 0 END)            AS NUMERATOR,      -- залилан
       COUNT(*)                                                     AS DENOMINATOR,    -- нийт гүйлгээ
       SUM(CASE WHEN x.IS_FRAUD = 'Y' THEN 1 ELSE 0 END) / COUNT(*) AS VALUE
FROM   {{schema.cardzone}}.CARD_TXN x
JOIN   {{schema.cardzone}}.TERMINAL t ON t.TERMINAL_ID = x.TERMINAL_ID
WHERE  x.TXN_DATE >= :p_period_start
  AND  x.TXN_DATE <  :p_report_date_next
GROUP  BY t.SOL_ID

/* ═══ ClickHouse-д шалгах ══════════════════════════════════════════════════════════════════════
   Энэ comment-ийг runner ажиллуулахгүй. Доорх query-г ClickHouse дээр хуулж ажиллуулна:
   DBeaver «RA ClickHouse — үр дүн (local docker)» холболт, эсвэл http://localhost:8123/play
   (Query-г энэ файлд uncomment хийхгүй — тэгвэл Oracle дээр SQL-тэй хамт ажиллаж алдаа өгнө.)

   1) Run-ээс ӨМНӨ   (а) → status = БАЙХГҮЙ, rows = 0      (б) → хоосон
   2) Ажиллуулах     python ri.py run --env local activities/act_97_practice/ri_97_9005.sql -p 2026-Q3
   3) Run-ий ДАРАА   (а) → status = БАЙНА, rows = 1        (б) → салбарын сүлжээний (1500) утга, оноо, SOLID-ууд
                     (в) SOL бүрийн задаргаа ri_result-д хадгалагдахгүй: run … --save-csv → output/local/ri_97_9005_20260930.csv
                     Дахин run хийвэл rows хэвээр (хуучин мөр ri_history-д шилжинэ — давхардахгүй)
   4) Тулгах         python ri.py verify --env local activities/act_97_practice/ri_97_9005.sql -p 2026-Q3

-- (а) ri_result-д орсон эсэх
SELECT if(count() = 0, 'БАЙХГҮЙ', 'БАЙНА') AS status, count() AS rows
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9005' AND snapshot_date = '2026-09-30';

-- (б) Үйл ажиллагааны (BRANCHID 1500) утга, оноо, SOLID-ууд
SELECT activity, activity_id, solid, branch_id, risk_indicator, risk_ind_id, result_number, result,
       snapshot_date, run_id, loaded_at
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9005' AND snapshot_date = '2026-09-30';
═════════════════════════════════════════════════════════════════════════════════════════════════ */
