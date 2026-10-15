/*---
indicator_id: RI_40_1526
name_mn: "Хүний нөөцийн нэг ажилтанд ногдох нийт ажилтнуудын тоо"
status: REVIEW
version: 1.0.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |    # харуулахад; оноо доорх scale-аар
  5-1:251-ээс дээш
  4-1:201-1:250
  3-1:151-1:200
  2-1:101-1:150
  1-1:100 эсвэл түүнээс доош
source_system: "ХНУГ"
required_info: "Хүний нөөцийн ажилтнуудын тоо"
method: "Нийт ажилтан/ХНУГ-ын менежер албан тушаалтай ажилтан"
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
data_mapping: "Хуучин"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Хүний нөөцийн нэг менежерт ногдох ажилтан (банк нийт): тайлант өдөр ажиллаж буй нийт ажилтан ÷ энэ үйл
  ажиллагааны (ХНУГ, :p_activity_branch_id = BRANCHID) SOL-ууд дахь "менежер" албан тушаалтан. VALUE = N (1:N).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
# Мастерийн "1:251-ээс дээш" бичиглэлийг parser задлахгүй тул шатлалыг гараар (VALUE = N):
scale:
  type: numeric
  numericRules:
    - {max: 100.000000001, score: 1, label: "1:100 эсвэл түүнээс доош"}
    - {min: 100.000000001, max: 150.000000001, score: 2, label: "1:101-1:150"}
    - {min: 150.000000001, max: 200.000000001, score: 3, label: "1:151-1:200"}
    - {min: 200.000000001, max: 250.000000001, score: 4, label: "1:201-1:250"}
    - {min: 250.000000001, score: 5, label: "1:251-ээс дээш"}
---*/
WITH emp AS (
    SELECT e.EMPLOYEE_ID, e.SOLID, e.POSITION_NAME
    FROM   {{shared.erp.employee_sol}} e
), hr_sol AS (
    SELECT u.SOLID
    FROM   {{shared.org.units}} u
    WHERE  u.BRANCHID = :p_activity_branch_id
), cnt AS (
    SELECT (SELECT COUNT(*) FROM emp)                               AS TOTAL_EMP,
           (SELECT COUNT(*) FROM emp e
            WHERE  e.SOLID IN (SELECT h.SOLID FROM hr_sol h)
              AND  UPPER(e.POSITION_NAME) LIKE '%МЕНЕЖЕР%')          AS HR_MANAGERS
    FROM   DUAL
)
SELECT 'BANK'                                                       AS ENTITY_LEVEL,
       'BANK'                                                       AS ENTITY_ID,
       'Банк нийт'                                                  AS ENTITY_NAME,
       c.TOTAL_EMP                                                  AS NUMERATOR,      -- нийт ажилтан
       c.HR_MANAGERS                                                AS DENOMINATOR,    -- ХН менежер
       c.TOTAL_EMP / NULLIF(c.HR_MANAGERS, 0)                       AS VALUE
FROM   cnt c
