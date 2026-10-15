-- Тайлант өдөр (:p_report_date) ажиллаж байгаа ажилтан: SOLID, албан тушаал (ERP — баганын нэр ТААМАГ).
-- Ажиллаж байгаа = EMPLOYEE_HISTORY-ийн START_DATE <= өдөр <= NVL(END_DATE, ∞) (тухайн өдрийг оруулна).
-- ERP_HR_CURRENT_STATUS нь зөвхөн өнөөдрийн төлөв тул түүхэн тайлант өдөрт ашиглахгүй.
-- Буцаах: EMPLOYEE_ID, SOLID, POSITION_ID, POSITION_NAME, IS_MANAGER (Y/N), HIRE_DATE (банкинд орсон),
--         POSITION_START (одоогийн албан тушаалд томилогдсон)
SELECT h.EMPLOYEE_ID           AS EMPLOYEE_ID,
       d.SOLID                 AS SOLID,
       h.POSITION_ID           AS POSITION_ID,
       p.POSITION_NAME         AS POSITION_NAME,
       p.IS_MANAGER            AS IS_MANAGER,
       e.HIRE_DATE             AS HIRE_DATE,
       h.START_DATE            AS POSITION_START
FROM   {{schema.erp}}.EMPLOYEE_HISTORY h
JOIN   {{schema.erp}}.HR_ORG_DEPARTMENT d ON d.DEPARTMENT_ID = h.DEPARTMENT_ID
JOIN   {{schema.erp}}.ERP_HR_POSITION p   ON p.POSITION_ID = h.POSITION_ID
JOIN   {{schema.erp}}.ERP_EMPLOYEE e      ON e.EMPLOYEE_ID = h.EMPLOYEE_ID
WHERE  h.START_DATE <= :p_report_date
  AND  (h.END_DATE IS NULL OR h.END_DATE >= :p_report_date)
