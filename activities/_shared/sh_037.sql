/*---
indicator_id: SH_037
name_mn: "Эргэн хяналтын чанар - Corp"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-0-59%
  4-60-69%
  3-70-79%
  2-80-89%
  1-90-100%
source_system: "ЗГ-ЗМХ"
required_info: "Өр цуглуулах, эргэн хяналт, ЗХБ, зээлийн материал буцаалтын үйл ажиллагааны тайлан"
method: "Зээлийн эргэн хяналтын чанарыг аудит орсноос хойшхи бүх улирлын дундаж үнэлгээгээр үнэлнэ."
period_text: "Аудит орсноос хойш"
automatable: "Тийм"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Зээлийн эргэн хяналтын чанар: аудит орсноос хойшхи БҮХ улирлын үнэлгээний дундаж
  (COREMIS.LOAN_MONITORING_QA, QUARTER_END [аудитын огноо, тайлант өдөр]). VALUE = харьцаа (0.82 = 82%).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(m.SOLID)                                             AS ENTITY_ID,
       SUM(m.SCORE_PCT) / 100                                       AS NUMERATOR,      -- үнэлгээний нийлбэр
       COUNT(*)                                                     AS DENOMINATOR,    -- улирал × SOL
       SUM(m.SCORE_PCT) / 100 / COUNT(*)                            AS VALUE
FROM   {{schema.coremis}}.LOAN_MONITORING_QA m
WHERE  m.QUARTER_END >= :p_period_start
  AND  m.QUARTER_END <= :p_report_date
GROUP  BY m.SOLID
