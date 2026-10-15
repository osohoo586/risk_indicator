/*---
indicator_id: SH_001
name_mn: "Ажилтнуудын ажилласан жилийн дундаж"
description: >
  Удирдах бус ажилтнуудын (ERP_HR_POSITION.IS_MANAGER = 'N') банкинд ажилласан жилийн дундаж, тайлант өдрөөр:
  Σ (тайлант өдөр − HIRE_DATE) / 365.25 ÷ ажилтны тоо. SOL бүрээр NUMERATOR = нийт жил, DENOMINATOR = тоо →
  үйл ажиллагааны SOL-уудаар Σ / Σ (жигнэсэн дундаж).
  Ашигладаг: RI_01_0025, RI_02_0073, RI_03_0124, RI_04_0162, RI_06_0241, RI_07_0278, RI_08_0314, RI_09_0350, RI_10_0382, RI_11_0417, RI_13_0483, RI_15_0559 …
connection: oracle_whouse
frequency: quarterly
period: report                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй
  1-1-2 жил
  2-2-3 жил
  3-3-4 жил
  4-4-5 жил
  5-0-1 жил and 5-с дээш жил
source_system: "ХНУГ"
required_info: |
  - Ажилтнуудын ажилласан жил
  - Ажилтнуудын тоо
method: |
  Ажилтнуудын ажилласан жилийн нийлбэр/Ажилтнуудын тоо.
  Удирдах бус ажилтнууд
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
data_mapping: "Хуучин"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                   AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                                        AS ENTITY_ID,
       SUM((:p_report_date - e.HIRE_DATE) / 365.25)            AS NUMERATOR,      -- нийт ажилласан жил
       COUNT(*)                                                AS DENOMINATOR,    -- удирдах бус ажилтан
       SUM((:p_report_date - e.HIRE_DATE) / 365.25) / COUNT(*) AS VALUE,          -- дундаж жил
       COUNT(*)                                                AS SOURCE_ROW_COUNT
FROM   {{shared.erp.employee_sol}} e
WHERE  e.IS_MANAGER = 'N'
GROUP  BY e.SOLID
