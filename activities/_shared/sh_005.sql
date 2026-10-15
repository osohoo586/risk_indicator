/*---
indicator_id: SH_005
name_mn: "Орон тоо бүрэн эсэх"
description: >
  Ажиллаж буй ажилтан ÷ батлагдсан орон тоо (ERP_HR_STAFF_PLAN, тайлант өдөр хүчинтэй). Удирдлага, ажилтнууд
  бүгд орно. Орон тоо батлагдаагүй SOL орохгүй. VALUE = харьцаа (1 = 100%).
  Ашигладаг: RI_01_0024, RI_02_0072, RI_03_0123, RI_04_0161, RI_06_0240, RI_07_0277, RI_08_0313, RI_09_0349, RI_10_0381, RI_11_0416, RI_13_0482, RI_15_0558 …
connection: oracle_whouse
frequency: quarterly
period: report                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй
  1-1
  2-95%-99%
  3-90%-94%
  4-85%-89%
  5-85%-с доош
source_system: "ХНУГ"
required_info: |
  - Батлагдсан орон тоо
  - Ажиллаж буй ажилтны тоо
method: "Ажиллаж буй ажилтны тоо/батлагдсан орон тоо. Удирдлага, ажилтнууд бүгд орно. Гэрээт ажилтны орон тоотой бол оруулж тооцно."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
data_mapping: "Хуучин"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH plan AS (
    SELECT d.SOLID, SUM(s.APPROVED_COUNT) AS APPROVED
    FROM   {{schema.erp}}.ERP_HR_STAFF_PLAN s
    JOIN   {{schema.erp}}.HR_ORG_DEPARTMENT d ON d.DEPARTMENT_ID = s.DEPARTMENT_ID
    WHERE  s.EFFECTIVE_FROM <= :p_report_date
      AND  (s.EFFECTIVE_TO IS NULL OR s.EFFECTIVE_TO >= :p_report_date)
    GROUP  BY d.SOLID
), act AS (
    SELECT e.SOLID, COUNT(*) AS CNT
    FROM   {{shared.erp.employee_sol}} e
    GROUP  BY e.SOLID
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(p.SOLID)                              AS ENTITY_ID,
       NVL(a.CNT, 0)                                 AS NUMERATOR,      -- ажиллаж буй
       p.APPROVED                                    AS DENOMINATOR,    -- батлагдсан орон тоо
       NVL(a.CNT, 0) / NULLIF(p.APPROVED, 0)         AS VALUE
FROM   plan p
LEFT   JOIN act a ON a.SOLID = p.SOLID
