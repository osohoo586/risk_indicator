/*---
indicator_id: SH_022
name_mn: "Мэдлэгийн түвшин"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score4"
scale_text: |
  1-95%-100%
  2-90%-94%
  3-85%-89%
  4-80%-84%
  5-80%-с доош
source_system: "ХНУГ,"
required_info: "Мэдлэгийн шалгалтын дүн Эрсдэл, Комплаенс,  Зээлийн үйл ажиллагааны журмын мэдлэг, МАБ"
method: "БТГ-ТТХ-ийн ажилтнуудын мэдлэгийн шалгалтын дүнг харгалзан үнэлнэ"
period_text: "Хамгийн сүүлд авсан шалгалтаар"
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Тайлант өдөр ажиллаж буй ажилтан бүрийн хамгийн сүүлийн мэдлэгийн шалгалтын дундаж (ERP_HR_KNOWLEDGE_TEST),
  SOL бүрээр. VALUE = харьцаа (0.91 = 91%).
connection: oracle_whouse
frequency: quarterly
period: latest                     # master-ийнхыг дарна: сүүлийн шалгалт
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH t AS (
    SELECT k.EMPLOYEE_ID, k.SCORE_PCT,
           ROW_NUMBER() OVER (PARTITION BY k.EMPLOYEE_ID ORDER BY k.TEST_DATE DESC, k.TEST_ID DESC) AS RN
    FROM   {{schema.erp}}.ERP_HR_KNOWLEDGE_TEST k
    WHERE  k.TEST_DATE <= :p_report_date
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                                             AS ENTITY_ID,
       SUM(t.SCORE_PCT) / 100                                       AS NUMERATOR,
       COUNT(*)                                                     AS DENOMINATOR,
       SUM(t.SCORE_PCT) / 100 / COUNT(*)                            AS VALUE
FROM   {{shared.erp.employee_sol}} e
JOIN   t ON t.EMPLOYEE_ID = e.EMPLOYEE_ID AND t.RN = 1
GROUP  BY e.SOLID
