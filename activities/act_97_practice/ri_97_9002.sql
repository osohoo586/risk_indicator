/*---
indicator_id: RI_97_9002
name_mn: Удирдах ажилтны эзлэх хувь
name_en: Share of managers
description: >
  ТУРШИЛТ — удирдах (захирал, кассын эрхлэгч, ахлах) ажилтны эзлэх хувь, тайлант өдрөөр. Хяналтын хүрээ
  (span of control) хэт өргөн бол эрсдэлтэй.
status: IN_PROGRESS
version: 0.1.0
scale_text: |
  5-10%-аас бага
  3-10%-19.9%
  1-20% ба түүнээс дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                                             AS ENTITY_ID,
       SUM(CASE WHEN e.IS_MANAGER = 'Y' THEN 1 ELSE 0 END)          AS NUMERATOR,      -- удирдах
       COUNT(*)                                                     AS DENOMINATOR,    -- бүх ажилтан
       SUM(CASE WHEN e.IS_MANAGER = 'Y' THEN 1 ELSE 0 END) / COUNT(*) AS VALUE
FROM   {{shared.erp.employee_sol}} e
GROUP  BY e.SOLID

/* ═══ ClickHouse-д шалгах ══════════════════════════════════════════════════════════════════════
   Энэ comment-ийг runner ажиллуулахгүй. Доорх query-г ClickHouse дээр хуулж ажиллуулна:
   DBeaver «RA ClickHouse — үр дүн (local docker)» холболт, эсвэл http://localhost:8123/play
   (Query-г энэ файлд uncomment хийхгүй — тэгвэл Oracle дээр SQL-тэй хамт ажиллаж алдаа өгнө.)

   1) Run-ээс ӨМНӨ   (а) → status = БАЙХГҮЙ, rows = 0      (б), (в) → хоосон
   2) Ажиллуулах     python ri.py run --env local activities/act_97_practice/ri_97_9002.sql -p 2026-Q3
   3) Run-ий ДАРАА   (а) → status = БАЙНА, rows = 1 + 12   (б) → салбарын сүлжээний (1500) утга, оноо, SOLID-ууд
                     (в) → SOL бүрийн удирдах / нийт
                     Дахин run хийвэл rows хэвээр (хуучин мөр ri_history-д шилжинэ — давхардахгүй)
   4) Тулгах         python ri.py verify --env local activities/act_97_practice/ri_97_9002.sql -p 2026-Q3

-- (а) ri_result-д орсон эсэх
SELECT if(count() = 0, 'БАЙХГҮЙ', 'БАЙНА') AS status, count() AS rows
FROM   risk_assessment_local.ri_result
WHERE  indicator_id = 'RI_97_9002' AND report_date = '2026-09-30';

-- (б) Үйл ажиллагааны (BRANCHID 1500) утга, оноо
SELECT indicator_id, ra_name, branch_id, sol_id, scale, scale_text, numerator, denominator, score, last_workdate,
       file_name, run_id, loaded_at
FROM   risk_assessment_local.v_risk_indicators
WHERE  indicator_id = 'RI_97_9002' AND last_workdate = '2026-09-30';

-- (в) Задаргаа (SOL бүрээр)
SELECT entity_level, entity_id, entity_name, numerator, denominator, value, value_text
FROM   risk_assessment_local.ri_result
WHERE  indicator_id = 'RI_97_9002' AND report_date = '2026-09-30' AND entity_level != 'ACTIVITY'
ORDER  BY entity_id;
═════════════════════════════════════════════════════════════════════════════════════════════════ */
