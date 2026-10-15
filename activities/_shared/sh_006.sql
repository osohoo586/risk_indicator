/*---
indicator_id: SH_006
name_mn: "Удирдах ажилтны ажилласан жилийн дундаж"
description: >
  Удирдах ажилтнуудын (IS_MANAGER = 'Y') ОДООГИЙН албан тушаалдаа ажилласан жилийн дундаж:
  Σ (тайлант өдөр − POSITION_START) / 365.25 ÷ тоо. POSITION_START = EMPLOYEE_HISTORY-ийн одоогийн мөрийн
  START_DATE (шилжүүлэн томилсон бол шинэ мөр).
  Ашигладаг: RI_01_0026, RI_02_0074, RI_03_0125, RI_04_0163, RI_06_0242, RI_07_0279, RI_08_0315, RI_09_0351, RI_10_0383, RI_11_0418, RI_13_0484, RI_15_0560 …
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
  3-3-3.5 жил
  4-3.5-4 жил
  5-0-1 жил and 4-с дээш жил/удирдлага байхгүй/Захирал нь өөр банкнаас томилогдсон.
source_system: "ХНУГ"
required_info: |
  - Удирдах ажилтнуудын тухайн албан тушаалд тохиолгдсон огноо
  - Удирдах ажилтны тоо
method: "- Удирдах ажилтнуудын тухайн албан тушаалдаа ажилласан жилийн нийлбэр/Ажилтнуудын тоо"
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
data_mapping: "Хуучин"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                                             AS ENTITY_ID,
       SUM((:p_report_date - e.POSITION_START) / 365.25)            AS NUMERATOR,
       COUNT(*)                                                     AS DENOMINATOR,
       SUM((:p_report_date - e.POSITION_START) / 365.25) / COUNT(*) AS VALUE,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{shared.erp.employee_sol}} e
WHERE  e.IS_MANAGER = 'Y'
GROUP  BY e.SOLID
