/*---
indicator_id: SH_020
name_mn: "Follow up үнэлгээ"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score3"
scale_text: |
  0-Үнэлэхгүй
  1-95%-100%
  2-90%-94%
  3-85%-89%
  4-80%-84%
  5-80%-с доош
source_system: "ДАГ, Auditsolution"
required_info: "- Өмнөх аудитын зөвлөмжийн хэрэгжилтийн баталгаажуулалтын үр дүн."
method: "- Дагах аудитын үнэлгээгээр үнэлнэ."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Сүүлийн дотоод аудитын зөвлөмжөөс хэрэгжүүлэх хугацаа нь тайлант өдрөөс өмнө болсон нь хэдэн хувь
  хугацаандаа хэрэгжсэн (CLOSED_DATE ≤ DUE_DATE). Хугацаа болсон зөвлөмж алга → Үнэлэхгүй.
connection: oracle_whouse
frequency: quarterly
period: latest                     # master-ийнхыг дарна: сүүлийн аудитыг өөрөө үнэлнэ
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH f AS (
    SELECT la.BRANCHID,
           SUM(CASE WHEN x.STATUS = 'ХЭРЭГЖСЭН' AND x.CLOSED_DATE <= x.DUE_DATE THEN 1 ELSE 0 END) AS DONE,
           COUNT(*) AS DUE
    FROM   {{shared.grc.last_audit}} la
    JOIN   {{schema.grc}}.AUDIT_FINDING x ON x.ENGAGEMENT_ID = la.ENGAGEMENT_ID
    WHERE  x.DUE_DATE <= :p_report_date
    GROUP  BY la.BRANCHID
)
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       f.DONE                                                       AS NUMERATOR,      -- хугацаандаа хэрэгжсэн
       f.DUE                                                        AS DENOMINATOR,    -- хугацаа нь болсон
       f.DONE / NULLIF(f.DUE, 0)                                    AS VALUE,
       CASE WHEN f.DUE IS NULL THEN 'Үнэлэхгүй' END                 AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN f ON f.BRANCHID = b.BRANCHID
