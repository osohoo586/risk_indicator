/*---
indicator_id: SH_015
name_mn: "Монгол банкны үнэлгээ"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй /МБ-ны шалгалт ороогүй /
  1-Сайн
  2-Хэвийн
  3-Дунд
  4-Хангалтгүй
  5-Муу
source_system: "Дотоод аудитын газрын захирал"
required_info: "- Монгол банкны баталгаажуулалтын үр дүн"
method: "- Монгол банкны шалгалтын үр дүнгээс тухайн үйл ажиллагаатай холбоотой үнэлгээг шүүнэ."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойшхи хамгийн сүүлийн Монгол банкны шалгалтын үнэлгээ (GRC.EXTERNAL_REVIEW, REVIEWER = МБ):
  RESULT_CODE 1 Сайн … 5 Муу. Шалгалт ороогүй → Үнэлэхгүй.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH r AS (
    SELECT x.BRANCHID, x.RESULT_CODE,
           ROW_NUMBER() OVER (PARTITION BY x.BRANCHID ORDER BY x.REVIEW_DATE DESC, x.REVIEW_ID DESC) AS RN
    FROM   {{schema.grc}}.EXTERNAL_REVIEW x
    WHERE  x.REVIEWER = 'МБ'
      AND  x.REVIEW_DATE >= :p_period_start
      AND  x.REVIEW_DATE <  :p_report_date_next
)
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE r.RESULT_CODE WHEN 1 THEN 'Сайн' WHEN 2 THEN 'Хэвийн' WHEN 3 THEN 'Дунд' WHEN 4 THEN 'Хангалтгүй'
                          WHEN 5 THEN 'Муу' ELSE 'Үнэлэхгүй /МБ-ны шалгалт ороогүй /' END AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN r ON r.BRANCHID = b.BRANCHID AND r.RN = 1
