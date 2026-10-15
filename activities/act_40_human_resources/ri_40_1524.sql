/*---
indicator_id: RI_40_1524
name_mn: "Ажилтнуудын ажлын гүйцэтгэлийн дундаж үнэлгээ"
status: REVIEW
version: 1.0.0
# ── Master ──
weight: 1                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-84% ба түүнээс доош
  4-85%-89%
  3-90%-94%
  2-95%-99%
  1-100% ба түүнээс дээш
source_system: "ХНУГ, СУГ-метрик"
required_info: "Нийт ажилтнуудын дундаж  гүйцэтгэл"
method: "Нийт ажилтны үнэлгээний нийлбэр/Ажилтны тоо"
period_text: "Аудит орсноос хойш улирлын дундаж"
automatable: "Тийм"
data_mapping: "Хуучин"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Ажилтнуудын гүйцэтгэлийн дундаж үнэлгээ (банк нийт): аудит орсноос хойшхи улирал бүрийн дундаж
  (ERP_HR_APPRAISAL, PERIOD_END [аудитын огноо, тайлант өдөр]) — улирлын дунджуудын дундаж.
  VALUE = харьцаа (0.93 = 93%).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH q AS (
    SELECT a.PERIOD_END, AVG(a.SCORE_PCT) AS AVG_PCT
    FROM   {{schema.erp}}.ERP_HR_APPRAISAL a
    WHERE  a.PERIOD_END >= :p_period_start
      AND  a.PERIOD_END <= :p_report_date
    GROUP  BY a.PERIOD_END
)
SELECT 'BANK'                                                       AS ENTITY_LEVEL,
       'BANK'                                                       AS ENTITY_ID,
       'Банк нийт'                                                  AS ENTITY_NAME,
       SUM(q.AVG_PCT) / 100                                         AS NUMERATOR,      -- улирлын дунджуудын нийлбэр
       COUNT(*)                                                     AS DENOMINATOR,    -- улирлын тоо
       SUM(q.AVG_PCT) / 100 / NULLIF(COUNT(*), 0)                   AS VALUE
FROM   q
