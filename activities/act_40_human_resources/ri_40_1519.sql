/*---
indicator_id: RI_40_1519
name_mn: "Банкны удирдах ажилтнуудын хүний нөөцийн эргэц"
status: REVIEW
version: 1.0.0
# ── Master ──
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-15-с дээш хувь
  4-13-14.9%
  3-11-12.9%
  2-9-10.9%
  1-9%-аас бага
source_system: "ХНУГ"
required_info: "Сүүлийн 1 жилийн хугацаанд ажлаас чөлөөлөгдсөн удирдах ажилтнуудын жагсаалт"
method: |
  - Ажлаас гарсан удирдах ажилтнуудын тоо / Ажилтны дундаж тоо.
  - Ажилтны дундаж тоо = (Тайлант хугацааны эхэнд байгаа ажилтан + тайлант хугацааны эцэст байгаа ажилтан)/2
  - Удирдах ажилтанд. Ахлах, захирал, кассын эрхлэгч нар орно
period_text: "Сүүлийн 1 жил"
automatable: "Тийм"
data_mapping: "Хуучин"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Банкны УДИРДАХ ажилтнуудын эргэц (банк нийт, сүүлийн 1 жил): гарсан удирдах ажилтан ÷ ((эхэнд + эцэст) / 2).
  Удирдах = ERP_HR_POSITION.IS_MANAGER = 'Y' (захирал, ахлах, кассын эрхлэгч). shared/erp/sol_flow.sql-ийн _MGR
  баганууд — RI_40_1520, SH_007-той НЭГ код. ENTITY_LEVEL = BANK: үйл ажиллагааны SOL биш, банк нийтээр.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'BANK'                                                       AS ENTITY_LEVEL,
       'BANK'                                                       AS ENTITY_ID,
       'Банк нийт'                                                  AS ENTITY_NAME,
       SUM(f.SEPARATIONS_MGR)                                        AS NUMERATOR,      -- гарсан
       (SUM(f.HC_START_MGR) + SUM(f.HC_END_MGR)) / 2                  AS DENOMINATOR,    -- дундаж тоо
       SUM(f.SEPARATIONS_MGR) / NULLIF((SUM(f.HC_START_MGR) + SUM(f.HC_END_MGR)) / 2, 0) AS VALUE
FROM   {{shared.erp.sol_flow}} f
