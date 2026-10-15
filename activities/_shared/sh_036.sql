/*---
indicator_id: SH_036
name_mn: "Зээлийн эрсдэлийн сан/Чанаргүй зээл"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-70% ба түүнээс доош
  4-71%-73%
  3-74%-77%
  2-77%-80%
  1-80% ба түүнээс дээш
source_system: "BI тайлангийн систем"
required_info: "Зээлийн үлдэгдлийн мэдээлэл, ЗТУБХС"
method: "Зээлийн эрсдэлийн сан/Чанаргүй зээл"
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Зээлийн эрсдэлийн сан (бүх зээлийн PROVISION_AMT) / чанаргүй зээлийн үлдэгдэл, тайлант өдрөөр, SOL бүрээр.
  Чанаргүй зээлгүй SOL-д DENOMINATOR 0 — үйл ажиллагааны Σ / Σ-д зөвхөн тоологчид орно.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(b.SOL_ID)                                            AS ENTITY_ID,
       SUM(b.PROVISION_AMT)                                         AS NUMERATOR,      -- эрсдэлийн сан
       SUM(CASE WHEN b.CLASS_CODE IN ('ХЭВИЙН БУС', 'ЭРГЭЛЗЭЭТЭЙ', 'МУУ') THEN b.OUTSTANDING_AMT ELSE 0 END)
                                                                    AS DENOMINATOR,    -- чанаргүй зээл
       SUM(b.PROVISION_AMT)
           / NULLIF(SUM(CASE WHEN b.CLASS_CODE IN ('ХЭВИЙН БУС', 'ЭРГЭЛЗЭЭТЭЙ', 'МУУ')
                             THEN b.OUTSTANDING_AMT ELSE 0 END), 0) AS VALUE,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{shared.finacle.loan_book}} b
GROUP  BY b.SOL_ID
