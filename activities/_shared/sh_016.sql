/*---
indicator_id: SH_016
name_mn: "Хөндлөнгийн аудитын зөвлөмж"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй /Хөндлөнгийн аудит/
  1-Бага эрсдэлтэй зөвлөмж өгсөн /Зөвлөмж өгөөгүй
  3-Дунд эрсдэлтэй зөвлөмж өгсөн
  5-Өндөр эрсдэлтэй зөвлөмж өгсөн
source_system: "Дотоод аудитын газрын захирал"
required_info: "- Хөндлөнгийн аудитын баталгаажуулалтын үр дүн"
method: "- Хөндлөнгийн аудитын үр дүнгээс тухайн үйл ажиллагаатай холбоотой зөвлөмжийг шүүнэ."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойшхи хөндлөнгийн аудитын хамгийн өндөр эрсдэлтэй зөвлөмж (GRC.EXTERNAL_REVIEW, RESULT_CODE 1 бага,
  3 дунд, 5 өндөр). Хөндлөнгийн аудит ороогүй → Үнэлэхгүй.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH r AS (
    SELECT x.BRANCHID, MAX(x.RESULT_CODE) AS CODE
    FROM   {{schema.grc}}.EXTERNAL_REVIEW x
    WHERE  x.REVIEWER = 'ХӨНДЛӨНГИЙН АУДИТ'
      AND  x.REVIEW_DATE >= :p_period_start
      AND  x.REVIEW_DATE <  :p_report_date_next
    GROUP  BY x.BRANCHID
)
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE r.CODE WHEN 1 THEN 'Бага эрсдэлтэй зөвлөмж өгсөн' WHEN 3 THEN 'Дунд эрсдэлтэй зөвлөмж өгсөн'
                   WHEN 5 THEN 'Өндөр эрсдэлтэй зөвлөмж өгсөн' ELSE 'Үнэлэхгүй /Хөндлөнгийн аудит/' END AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN r ON r.BRANCHID = b.BRANCHID
