/*---
indicator_id: RI_97_9004
name_mn: Хугацаа хэтэрсэн ба чанаргүй зээлийн хувь
name_en: Past-due and non-performing loan share
description: >
  ТУРШИЛТ — ХЭВИЙН-ээс бусад ангилалтай зээлийн үлдэгдэл / нийт зээл, тайлант өдрөөр
  (shared/finacle/loan_book.sql — RI_01_0009, 0010-тай ижил хэсэг).
status: IN_PROGRESS
version: 0.1.0
scale_text: |
  1-5%-аас бага
  2-5%-7.9%
  3-8%-9.9%
  4-10%-14.9%
  5-15% ба түүнээс дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(b.SOL_ID)                                            AS ENTITY_ID,
       SUM(CASE WHEN b.CLASS_CODE != 'ХЭВИЙН' THEN b.OUTSTANDING_AMT ELSE 0 END) AS NUMERATOR,
       SUM(b.OUTSTANDING_AMT)                                       AS DENOMINATOR,
       SUM(CASE WHEN b.CLASS_CODE != 'ХЭВИЙН' THEN b.OUTSTANDING_AMT ELSE 0 END)
           / NULLIF(SUM(b.OUTSTANDING_AMT), 0)                      AS VALUE,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{shared.finacle.loan_book}} b
GROUP  BY b.SOL_ID

/* ═══ ClickHouse-д шалгах ══════════════════════════════════════════════════════════════════════
   Энэ comment-ийг runner ажиллуулахгүй. Доорх query-г ClickHouse дээр хуулж ажиллуулна:
   DBeaver «RA ClickHouse — үр дүн (local docker)» холболт, эсвэл http://localhost:8123/play
   (Query-г энэ файлд uncomment хийхгүй — тэгвэл Oracle дээр SQL-тэй хамт ажиллаж алдаа өгнө.)

   1) Run-ээс ӨМНӨ   (а) → status = БАЙХГҮЙ, rows = 0      (б) → хоосон
   2) Ажиллуулах     python ri.py run --env local activities/act_97_practice/ri_97_9004.sql -p 2026-Q3
   3) Run-ий ДАРАА   (а) → status = БАЙНА, rows = 1        (б) → салбарын сүлжээний (1500) утга, оноо, SOLID-ууд
                     (в) SOL бүрийн задаргаа ri_result-д хадгалагдахгүй: run … --save-csv → output/local/ri_97_9004_20260930.csv
                     Дахин run хийвэл rows хэвээр (хуучин мөр ri_history-д шилжинэ — давхардахгүй)
   4) Тулгах         python ri.py verify --env local activities/act_97_practice/ri_97_9004.sql -p 2026-Q3

-- (а) ri_result-д орсон эсэх
SELECT if(count() = 0, 'БАЙХГҮЙ', 'БАЙНА') AS status, count() AS rows
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9004' AND snapshot_date = '2026-09-30';

-- (б) Үйл ажиллагааны (BRANCHID 1500) утга, оноо, SOLID-ууд
SELECT activity, activity_id, solid, branch_id, risk_indicator, risk_ind_id, result_number, result,
       snapshot_date, run_id, loaded_at
FROM   risk_assessment_local.ri_result
WHERE  risk_ind_id = 'RI_97_9004' AND snapshot_date = '2026-09-30';
═════════════════════════════════════════════════════════════════════════════════════════════════ */
