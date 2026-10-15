/*---
indicator_id: RI_97_9001
name_mn: Туршлага багатай ажилтны хувь
name_en: Share of inexperienced staff
description: >
  ТУРШИЛТ — туршлага багатай ажилтан олон бол алдаа, залилангийн эрсдэл өндөр. Тайлант өдөр ажиллаж буй
  ажилтнаас банкинд 24 сараас бага ажилласан нь (shared/erp/employee_sol.sql), SOL бүрээр.
status: IN_PROGRESS
version: 0.1.0
value_range: {min: 0, max: 1}
scale_text: |
  1-10%-аас бага
  2-10%-19.9%
  3-20%-29.9%
  4-30% ба түүнээс дээш
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                                             AS ENTITY_ID,
       SUM(CASE WHEN e.HIRE_DATE > ADD_MONTHS(:p_report_date, -24) THEN 1 ELSE 0 END) AS NUMERATOR,  -- < 2 жил
       COUNT(*)                                                     AS DENOMINATOR,                  -- бүх ажилтан
       SUM(CASE WHEN e.HIRE_DATE > ADD_MONTHS(:p_report_date, -24) THEN 1 ELSE 0 END) / COUNT(*) AS VALUE
FROM   {{shared.erp.employee_sol}} e
GROUP  BY e.SOLID

/* ═══ ClickHouse-д шалгах ══════════════════════════════════════════════════════════════════════
   Энэ comment-ийг runner ажиллуулахгүй. Доорх query-г ClickHouse дээр хуулж ажиллуулна:
   DBeaver «RA ClickHouse — үр дүн (local docker)» холболт, эсвэл http://localhost:8123/play
   (Query-г энэ файлд uncomment хийхгүй — тэгвэл Oracle дээр SQL-тэй хамт ажиллаж алдаа өгнө.)

   1) Run-ээс ӨМНӨ   (а) → status = БАЙХГҮЙ, rows = 0      (б), (в) → хоосон
   2) Ажиллуулах     python ri.py run --env local activities/act_97_practice/ri_97_9001.sql -p 2026-Q3
   3) Run-ий ДАРАА   (а) → status = БАЙНА, rows = 1 + 12   (б) → салбарын сүлжээний (1500) утга, оноо, SOLID-ууд
                     (в) → 12 салбарын SOL бүрийн тоологч / хуваарь
                     Дахин run хийвэл rows хэвээр (хуучин мөр ri_history-д шилжинэ — давхардахгүй)
   4) Тулгах         python ri.py verify --env local activities/act_97_practice/ri_97_9001.sql -p 2026-Q3

-- (а) ri_result-д орсон эсэх
SELECT if(count() = 0, 'БАЙХГҮЙ', 'БАЙНА') AS status, count() AS rows
FROM   risk_assessment_local.ri_result
WHERE  indicator_id = 'RI_97_9001' AND report_date = '2026-09-30';

-- (б) Үйл ажиллагааны (BRANCHID 1500) утга, оноо
SELECT indicator_id, ra_name, branch_id, sol_id, scale, scale_text, numerator, denominator, score, last_workdate,
       file_name, run_id, loaded_at
FROM   risk_assessment_local.v_risk_indicators
WHERE  indicator_id = 'RI_97_9001' AND last_workdate = '2026-09-30';

-- (в) Задаргаа (SOL бүрээр)
SELECT entity_level, entity_id, entity_name, numerator, denominator, value, value_text
FROM   risk_assessment_local.ri_result
WHERE  indicator_id = 'RI_97_9001' AND report_date = '2026-09-30' AND entity_level != 'ACTIVITY'
ORDER  BY entity_id;
═════════════════════════════════════════════════════════════════════════════════════════════════ */
