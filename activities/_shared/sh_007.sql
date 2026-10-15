/*---
indicator_id: SH_007
name_mn: "Хүний нөөцийн эргэц"
description: >
  Сүүлийн 1 жилд ажлаас гарсан ÷ ажилтны дундаж тоо ((эхэнд + эцэст) / 2) — shared/erp/sol_flow.sql.
  SOL бүрээр NUMERATOR = гарсан, DENOMINATOR = дундаж → үйл ажиллагааны SOL-уудаар Σ / Σ.
  Ашигладаг: RI_01_0027, RI_02_0075, RI_03_0126, RI_04_0164, RI_06_0243, RI_07_0280, RI_08_0316, RI_09_0352, RI_10_0384, RI_11_0419, RI_13_0485, RI_15_0561 …
connection: oracle_whouse
frequency: quarterly
period: last_year                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй
  1-10%-аас бага
  2-10%-12%
  3-13%-15%
  4-16%-19%
  5-20% болон түүнээс дээш
source_system: "ХНУГ"
required_info: |
  - Тайлант хугацаагаар ажиллаж буй ажилтны тоо
  - Тайлант хугацаанаас 1 жилийн өмнө ажиллаж байсан ажилтны тоо
method: |
  - Ажлаас гарсан ажилтнуудын тоо / Ажилтны дундаж тоо.
  - Ажилтны дундаж тоо = (Тайлант хугацааны эхэнд байгаа ажилтан + тайлант хугацааны эцэст байгаа ажилтан)/2
  - 1 жилийн өмнөх ажиллаж байсан ажилтны тоог боломжтой тохиолдолд өмнөх эрсдэлийн үнэлгээний файлаас авна. ДАГ-Дотоод Share
period_text: "Сүүлийн 1 жил"
automatable: "Тийм"
data_mapping: "Хуучин"
period: last_year                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                  AS ENTITY_LEVEL,
       TO_CHAR(f.SOLID)                                       AS ENTITY_ID,
       f.SEPARATIONS                                          AS NUMERATOR,      -- гарсан
       (f.HC_START + f.HC_END) / 2                            AS DENOMINATOR,    -- дундаж тоо
       f.SEPARATIONS / NULLIF((f.HC_START + f.HC_END) / 2, 0) AS VALUE
FROM   {{shared.erp.sol_flow}} f
