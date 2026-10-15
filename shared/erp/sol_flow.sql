-- SOLID бүрийн ажилтны урсгал [:p_period_start, :p_report_date] (хоёр өдрийг оруулна) — эргэцийн тооцоо.
--   HC_START / HC_END   эхний / сүүлийн өдөр ажиллаж байсан (EMPLOYEE_HISTORY-ийн идэвхтэй мөр)
--   SEPARATIONS         хугацаанд банкнаас гарсан (ERP_EMPLOYEE.END_DATE), гарах өдрийн SOLID-д
--   *_MGR               удирдах албан тушаалтан (ERP_HR_POSITION.IS_MANAGER = 'Y': захирал, ахлах, кассын эрхлэгч)
-- Дотоод шилжилт (TRANSFER), дэвшүүлэлт (PROMOTION) гаралт биш. Эргэц = SEPARATIONS / ((HC_START + HC_END) / 2).
-- Ашигладаг: SH_007 (SOL бүрээр), RI_40_1519, RI_40_1520 (банк нийт)
WITH asg AS (
    SELECT d.SOLID, p.IS_MANAGER, h.START_DATE, h.END_DATE, e.END_DATE AS EMP_END_DATE
    FROM   {{schema.erp}}.EMPLOYEE_HISTORY h
    JOIN   {{schema.erp}}.HR_ORG_DEPARTMENT d ON d.DEPARTMENT_ID = h.DEPARTMENT_ID
    JOIN   {{schema.erp}}.ERP_HR_POSITION p   ON p.POSITION_ID = h.POSITION_ID
    JOIN   {{schema.erp}}.ERP_EMPLOYEE e      ON e.EMPLOYEE_ID = h.EMPLOYEE_ID
), flags AS (
    SELECT a.SOLID, a.IS_MANAGER,
           CASE WHEN a.START_DATE <= :p_period_start
                 AND (a.END_DATE IS NULL OR a.END_DATE >= :p_period_start) THEN 1 ELSE 0 END AS AT_START,
           CASE WHEN a.START_DATE <= :p_report_date
                 AND (a.END_DATE IS NULL OR a.END_DATE >= :p_report_date) THEN 1 ELSE 0 END AS AT_END,
           CASE WHEN a.EMP_END_DATE >= :p_period_start AND a.EMP_END_DATE <= :p_report_date
                 AND a.START_DATE <= a.EMP_END_DATE
                 AND (a.END_DATE IS NULL OR a.END_DATE >= a.EMP_END_DATE) THEN 1 ELSE 0 END AS SEPARATED
    FROM   asg a
)
SELECT f.SOLID                                                        AS SOLID,
       SUM(f.AT_START)                                                AS HC_START,
       SUM(f.AT_END)                                                  AS HC_END,
       SUM(f.SEPARATED)                                               AS SEPARATIONS,
       SUM(CASE WHEN f.IS_MANAGER = 'Y' THEN f.AT_START ELSE 0 END)   AS HC_START_MGR,
       SUM(CASE WHEN f.IS_MANAGER = 'Y' THEN f.AT_END ELSE 0 END)     AS HC_END_MGR,
       SUM(CASE WHEN f.IS_MANAGER = 'Y' THEN f.SEPARATED ELSE 0 END)  AS SEPARATIONS_MGR
FROM   flags f
GROUP  BY f.SOLID
