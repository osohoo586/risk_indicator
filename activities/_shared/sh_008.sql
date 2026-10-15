/*---
indicator_id: SH_008
name_mn: "Ёс зүйн зөрчил"
description: >
  Аудит орсноос хойш ёс зүйн зөрчлөөр сахилгын шийтгэл (ERP_HR_DISCIPLINE.CASE_TYPE = 'ЁС ЗҮЙ') авсан
  тохиолдлын тоо, шийтгэл авах өдрийн SOLID-оор. 0 → "Үгүй" (Үнэлэхгүй), > 0 → "Тийм" (5).
  Ашигладаг: RI_01_0030, RI_02_0078, RI_03_0129, RI_04_0167, RI_06_0246, RI_07_0283, RI_08_0319, RI_09_0355, RI_10_0387, RI_11_0422, RI_13_0488, RI_15_0564 …
connection: oracle_whouse
frequency: quarterly
period: since_audit                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
rollup_metrics: {value: sum}      # SOL-уудын VALUE-г нэмнэ (тоо)
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй /Үгүй/
  5-Тийм
source_system: "ХНУГ"
required_info: |
  - ХНХ-ийн сахилгын шийтгэлийн бүртгэл
  - ДАГ-ын гомдлын бүртгэл
method: "- Хүний нөөцийн сахилгын шийтгэлийн бүртгэл, Ес зүйн зөрчил гарч сахилгын шийтгэл ногдуулсан эсэхийг баталгаажуулна."
period_text: "Аудит орсноос хойш хугацаанд хуримтлуулж тооцно."
automatable: "Тийм"
data_mapping: "Салбар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH v AS (
    SELECT d.SOLID, COUNT(*) AS CNT
    FROM   {{schema.erp}}.ERP_HR_DISCIPLINE x
    JOIN   {{schema.erp}}.EMPLOYEE_HISTORY h
           ON  h.EMPLOYEE_ID = x.EMPLOYEE_ID
           AND h.START_DATE <= x.ACTION_DATE
           AND (h.END_DATE IS NULL OR h.END_DATE >= x.ACTION_DATE)
    JOIN   {{schema.erp}}.HR_ORG_DEPARTMENT d ON d.DEPARTMENT_ID = h.DEPARTMENT_ID
    WHERE  x.CASE_TYPE = 'ЁС ЗҮЙ'
      AND  x.ACTION_DATE >= :p_period_start
      AND  x.ACTION_DATE <  :p_report_date_next
    GROUP  BY d.SOLID
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(u.SOLID)                              AS ENTITY_ID,
       NVL(v.CNT, 0)                                 AS VALUE           -- зөрчлийн тоо
FROM   (SELECT DISTINCT d.SOLID FROM {{schema.erp}}.HR_ORG_DEPARTMENT d) u
LEFT   JOIN v ON v.SOLID = u.SOLID
