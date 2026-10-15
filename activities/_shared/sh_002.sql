/*---
indicator_id: SH_002
name_mn: "Ажилтнуудын ажлын гүйцэтгэлийн үнэлгээний дундаж"
description: >
  Сүүлийн үнэлгээгээр: тайлант өдрөөс өмнөх хамгийн сүүлийн үнэлгээний үе (ERP_HR_APPRAISAL.PERIOD_END)-ийн
  дундаж %, тайлант өдөр ажиллаж буй ажилтнуудаар. VALUE = харьцаа (0.93 = 93%).
  Ашигладаг: RI_01_0028, RI_02_0076, RI_03_0127, RI_04_0165, RI_06_0244, RI_07_0281, RI_08_0317, RI_09_0353, RI_10_0385, RI_11_0420, RI_13_0486, RI_15_0562 …
connection: oracle_whouse
frequency: quarterly
period: latest                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
source_system: "ХНУГ"
required_info: "БТГ-БТГ, СУГ-ББХХ-н нийт ажилтнуудын дундаж  гүйцэтгэл"
method: "Нийт ажилтны үнэлгээний нийлбэр/Ажилтны тоо"
period_text: "Сүүлийн үнэлгээгээр"
automatable: "Тийм"
data_mapping: "Хуучин"
period: latest                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH last_cycle AS (
    SELECT MAX(a.PERIOD_END) AS PERIOD_END
    FROM   {{schema.erp}}.ERP_HR_APPRAISAL a
    WHERE  a.PERIOD_END <= :p_report_date
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                              AS ENTITY_ID,
       SUM(a.SCORE_PCT) / 100                        AS NUMERATOR,      -- үнэлгээний нийлбэр (харьцаа)
       COUNT(*)                                      AS DENOMINATOR,    -- үнэлэгдсэн ажилтан
       SUM(a.SCORE_PCT) / 100 / COUNT(*)             AS VALUE,
       COUNT(*)                                      AS SOURCE_ROW_COUNT
FROM   {{shared.erp.employee_sol}} e
JOIN   {{schema.erp}}.ERP_HR_APPRAISAL a ON a.EMPLOYEE_ID = e.EMPLOYEE_ID
JOIN   last_cycle c                      ON c.PERIOD_END = a.PERIOD_END
GROUP  BY e.SOLID
