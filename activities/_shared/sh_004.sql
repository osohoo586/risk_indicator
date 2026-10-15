/*---
indicator_id: SH_004
name_mn: "Нэг ажилтанд ногдох сургалтын цаг"
description: >
  Сүүлийн 1 жилд суусан сургалтын цаг ÷ тайлант өдөр ажиллаж буй ажилтны тоо (ERP_HR_TRAINING, START_DATE
  [:p_period_start, :p_report_date]). Сургалтгүй ажилтан 0 цагаар тоологдоно.
  Ашигладаг: RI_01_0023, RI_02_0071, RI_03_0122, RI_04_0160, RI_06_0239, RI_07_0276, RI_08_0312, RI_09_0348, RI_10_0380, RI_11_0415, RI_13_0481, RI_15_0557 …
connection: oracle_whouse
frequency: quarterly
period: last_year                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  1-16 цагаас дээш
  2-14-15.9 цаг
  3-12-13.9 цаг
  4-10-11.9 цаг
  5-10 доош цаг
source_system: "ХНУГ - БТХ - Сургалт хөгжлийн алба"
required_info: |
  - Дотоод болон гадаад сургалтын мэдээлэл
  - Нийт ажилтны тоо
method: "БТГ-БТГ, СУГ-ББХХ"
period_text: "Сүүлийн 1 жил"
automatable: "Тийм"
data_mapping: "Хуучин"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH hrs AS (
    SELECT t.EMPLOYEE_ID, SUM(t.HOURS) AS HOURS
    FROM   {{schema.erp}}.ERP_HR_TRAINING t
    WHERE  t.START_DATE >= :p_period_start
      AND  t.START_DATE <  :p_report_date_next
    GROUP  BY t.EMPLOYEE_ID
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                              AS ENTITY_ID,
       NVL(SUM(h.HOURS), 0)                          AS NUMERATOR,      -- нийт цаг
       COUNT(*)                                      AS DENOMINATOR,    -- ажилтан
       NVL(SUM(h.HOURS), 0) / COUNT(*)               AS VALUE,
       COUNT(*)                                      AS SOURCE_ROW_COUNT
FROM   {{shared.erp.employee_sol}} e
LEFT   JOIN hrs h ON h.EMPLOYEE_ID = e.EMPLOYEE_ID
GROUP  BY e.SOLID
