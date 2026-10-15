/*---
indicator_id: SH_047
name_mn: "Салбар, тооцооны төвийн захирлуудын орон тоо сул байсан хугацаа"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-5 хоног
  2-6 - 10 хоног
  3-11- 20 хоног
  4-21-30 хоног
  5-30 хоногоос дээш
source_system: "ХНУГ"
required_info: "Орон тоо сул байсан хугацаа"
method: "Аудит орсноос хойш орон тоо сул байсан албан тушаалтнуудын дундаж хугацаагаар хэмжинэ"
period_text: "Аудит орсноос хойш"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойш салбарын захирлын орон тоо сул байсан дундаж хоног (банк нийт): ERP EMPLOYEE_HISTORY-д
  "Салбарын захирал" албан тушаалын дараалсан томилгооны хоорондох завсар (тайлант өдөр хүртэл үргэлжилж буйг ч
  тайлант өдөр хүртэл тооцно), завсар эхэлсэн өдөр [:p_period_start, :p_report_date]. Сул орон тоо гараагүй → 0.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH h AS (
    SELECT h.POSITION_ID, h.START_DATE, h.END_DATE,
           LAG(h.END_DATE) OVER (PARTITION BY h.POSITION_ID ORDER BY h.START_DATE)          AS PREV_END,
           ROW_NUMBER() OVER (PARTITION BY h.POSITION_ID ORDER BY h.START_DATE DESC)      AS RN_LAST
    FROM   {{schema.erp}}.EMPLOYEE_HISTORY h
    JOIN   {{schema.erp}}.ERP_HR_POSITION p ON p.POSITION_ID = h.POSITION_ID
    WHERE  p.POSITION_NAME = 'Салбарын захирал'
      AND  h.START_DATE <= :p_report_date
), gaps AS (
    SELECT h.PREV_END + 1 AS GAP_START, h.START_DATE - 1 AS GAP_END
    FROM   h
    WHERE  h.PREV_END IS NOT NULL AND h.START_DATE > h.PREV_END + 1
    UNION ALL
    SELECT h.END_DATE + 1, :p_report_date                    -- одоо ч сул (дараагийн томилгоо алга)
    FROM   h
    WHERE  h.RN_LAST = 1 AND h.END_DATE < :p_report_date
)
SELECT 'BANK'                                                       AS ENTITY_LEVEL,
       'BANK'                                                       AS ENTITY_ID,
       'Банк нийт'                                                  AS ENTITY_NAME,
       NVL(SUM(LEAST(g.GAP_END, :p_report_date) - g.GAP_START + 1) / NULLIF(COUNT(*), 0), 0) AS VALUE,   -- хоног
       COUNT(*)                                                     AS SOURCE_ROW_COUNT                  -- сул орон тоо
FROM   gaps g
WHERE  g.GAP_START >= :p_period_start
  AND  g.GAP_START <= :p_report_date
