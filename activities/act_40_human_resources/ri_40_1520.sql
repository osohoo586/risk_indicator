/*---
indicator_id: RI_40_1520
name_mn: "Банкны ажилтнуудын хүний нөөцийн эргэц"
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
required_info: "Сүүлийн 1 жилийн хугацаанд ажлаас чөлөөлөгдсөн ажилтнуудын жагсаалт"
method: |
  - Ажлаас гарсан ажилтнуудын тоо / Ажилтны дундаж тоо.
  - Ажилтны дундаж тоо = (Тайлант хугацааны эхэнд байгаа ажилтан + тайлант хугацааны эцэст байгаа ажилтан)/2
period_text: "Сүүлийн 1 жил"
automatable: "Тийм"
data_mapping: "Хуучин"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Банкны ажилтнуудын эргэц (банк нийт, сүүлийн 1 жил): гарсан ÷ ((эхэнд + эцэст) / 2). Нэг SOL-ын түвшний
  тооцоолол (SH_007, үйл ажиллагаа бүрт) ба банк нийтийн (энэ) нь НЭГ shared/erp/sol_flow.sql-ийг ашиглана.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'BANK'                                                       AS ENTITY_LEVEL,
       'BANK'                                                       AS ENTITY_ID,
       'Банк нийт'                                                  AS ENTITY_NAME,
       SUM(f.SEPARATIONS)                                        AS NUMERATOR,      -- гарсан
       (SUM(f.HC_START) + SUM(f.HC_END)) / 2                  AS DENOMINATOR,    -- дундаж тоо
       SUM(f.SEPARATIONS) / NULLIF((SUM(f.HC_START) + SUM(f.HC_END)) / 2, 0) AS VALUE
FROM   {{shared.erp.sol_flow}} f
