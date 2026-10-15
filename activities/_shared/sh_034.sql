/*---
indicator_id: SH_034
name_mn: "АХЗээл/нийт зээл"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-2.5% ба түүнээс бага
  2-2.5%-3.9%
  3-4%-5.4%
  4-5.5%-6.9%
  5-7% ба түүнээс дээш
source_system: "BI тайлангийн систем"
required_info: "Зээлийн үлдэгдлийн мэдээлэл"
method: "Анхаарал хандуулах зээл/Нийт зээл"
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Анхаарал хандуулах зээл (ангилал ХУГАЦАА ХЭТЭРСЭН) / нийт зээлийн үлдэгдэл, тайлант өдрөөр, SOL бүрээр
  (shared/finacle/loan_book.sql). Үйл ажиллагааны SOL-уудаар Σ АХЗ / Σ нийт.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(b.SOL_ID)                                            AS ENTITY_ID,
       SUM(CASE WHEN b.CLASS_CODE = 'ХУГАЦАА ХЭТЭРСЭН' THEN b.OUTSTANDING_AMT ELSE 0 END) AS NUMERATOR,   -- АХЗ
       SUM(b.OUTSTANDING_AMT)                                       AS DENOMINATOR,                         -- нийт зээл
       SUM(CASE WHEN b.CLASS_CODE = 'ХУГАЦАА ХЭТЭРСЭН' THEN b.OUTSTANDING_AMT ELSE 0 END)
           / NULLIF(SUM(b.OUTSTANDING_AMT), 0)                      AS VALUE,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{shared.finacle.loan_book}} b
GROUP  BY b.SOL_ID
