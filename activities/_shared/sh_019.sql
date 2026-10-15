/*---
indicator_id: SH_019
name_mn: "Өндөр эрсдэлтэй асуудлын тоо"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score3"
scale_text: |
  0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/
  1-10% хүртэл
  2-10%-14%
  3-15%-20%
  4-21%-25%
  5-25%-иас дээш
source_system: "ДАГ, Auditsolution"
required_info: "- Өмнөх аудитын RACM"
method: "- Өмнөх аудитын RACM-аас өндөр эрсдэлтэй асуудлын тоог тодорхойлно. Дотоод хяналт нь хангалтгүй үнэлэгдсэн эрсдэлийн үзүүлэлтийн тоо."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Сүүлийн дотоод аудитын асуудлаас өндөр эрсдэлтэйн хувь (GRC.AUDIT_FINDING.RISK_LEVEL = ӨНДӨР).
connection: oracle_whouse
frequency: quarterly
period: latest                     # master-ийнхыг дарна: сүүлийн аудитыг өөрөө үнэлнэ
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       CASE WHEN MAX(la.ENGAGEMENT_ID) IS NOT NULL
            THEN SUM(CASE WHEN f.RISK_LEVEL = 'ӨНДӨР' THEN 1 ELSE 0 END) END AS NUMERATOR,   -- өндөр эрсдэлтэй
       CASE WHEN MAX(la.ENGAGEMENT_ID) IS NOT NULL THEN COUNT(f.FINDING_ID) END AS DENOMINATOR, -- нийт асуудал
       SUM(CASE WHEN f.RISK_LEVEL = 'ӨНДӨР' THEN 1 ELSE 0 END) / NULLIF(COUNT(f.FINDING_ID), 0) AS VALUE,
       CASE WHEN MAX(la.ENGAGEMENT_ID) IS NULL THEN 'Үнэлэхгүй /Өмнө аудит хийж байгаагүй/' END AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN {{shared.grc.last_audit}} la ON la.BRANCHID = b.BRANCHID
LEFT   JOIN {{schema.grc}}.AUDIT_FINDING f ON f.ENGAGEMENT_ID = la.ENGAGEMENT_ID
GROUP  BY b.BRANCHID
