/*---
indicator_id: SH_035
name_mn: "Чанаргүй зээл/Нийт зээл"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-5% түүнээс дээш
  4-0.05
  3-4-4.9%
  2-3-3.9%
  1-3%-аас бага
source_system: "BI тайлангийн систем"
required_info: "Зээлийн үлдэгдлийн мэдээлэл, ЗТУБХС"
method: "Чанаргүй зээл/Нийт зээл"
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Чанаргүй зээл (ХЭВИЙН БУС + ЭРГЭЛЗЭЭТЭЙ + МУУ) / нийт зээлийн үлдэгдэл, тайлант өдрөөр, SOL бүрээр.
  МАСТЕР: шатлалын "4-0.05" мөр 5%-тай давхцаж 4 оноо хэзээ ч гарахгүй — мастерийг засах (5-7%?).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(b.SOL_ID)                                            AS ENTITY_ID,
       SUM(CASE WHEN b.CLASS_CODE IN ('ХЭВИЙН БУС', 'ЭРГЭЛЗЭЭТЭЙ', 'МУУ') THEN b.OUTSTANDING_AMT ELSE 0 END)
                                                                    AS NUMERATOR,      -- чанаргүй зээл
       SUM(b.OUTSTANDING_AMT)                                       AS DENOMINATOR,    -- нийт зээл
       SUM(CASE WHEN b.CLASS_CODE IN ('ХЭВИЙН БУС', 'ЭРГЭЛЗЭЭТЭЙ', 'МУУ') THEN b.OUTSTANDING_AMT ELSE 0 END)
           / NULLIF(SUM(b.OUTSTANDING_AMT), 0)                      AS VALUE,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{shared.finacle.loan_book}} b
GROUP  BY b.SOL_ID
