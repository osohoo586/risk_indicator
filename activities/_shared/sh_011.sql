/*---
indicator_id: SH_011
name_mn: "Бүтцийн өөрчлөлт хийгдсэн эсэх"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй /Үгүй/
  4-Алба
  5-Газар, хэлтэс
source_system: "ХНУГ-БТХ-БТА"
required_info: "Хамрах хугацаанд хийгдсэн бүтцийн өөрчлөлтийн мэдээлэл"
method: "- Аудит орсноос хойш бүтцийн өөрчлөлт хийгдсэн эсэхийг баталгаажуулах"
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойш (:p_period_start) үйл ажиллагааны бүтэц (COREMIS.MAIN-ийн SOLID-ууд) өөрчлөгдсөн эсэх:
  нэмэгдсэн / хасагдсан SOLID-ийн нэрэнд "алба" бол Алба (4), бусад (хэлтэс, газар) бол Газар, хэлтэс (5).
  Эхлэлийн өдөр snapshot байхгүй бол хамгийн эртнийх. Өөрчлөлтгүй → Үнэлэхгүй /Үгүй/.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH snap AS (
    SELECT NVL(MAX(CASE WHEN x.TDATE <= :p_period_start THEN x.TDATE END), MIN(x.TDATE)) AS T0,
           NVL(MAX(CASE WHEN x.TDATE <= :p_report_date THEN x.TDATE END), MIN(x.TDATE))  AS T1
    FROM   {{schema.main}}.MAIN x
), u0 AS (
    SELECT m.BRANCHID, m.SOLID, m.BRANCHNAME FROM {{schema.main}}.MAIN m JOIN snap s ON m.TDATE = s.T0
), u1 AS (
    SELECT m.BRANCHID, m.SOLID, m.BRANCHNAME FROM {{schema.main}}.MAIN m JOIN snap s ON m.TDATE = s.T1
), chg AS (
    SELECT NVL(u1.BRANCHID, u0.BRANCHID)     AS BRANCHID,
           NVL(u1.BRANCHNAME, u0.BRANCHNAME) AS SOLNAME
    FROM   u0 FULL OUTER JOIN u1 ON u1.BRANCHID = u0.BRANCHID AND u1.SOLID = u0.SOLID
    WHERE  u0.SOLID IS NULL OR u1.SOLID IS NULL
)
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE WHEN COUNT(c.SOLNAME) = 0 THEN 'Үнэлэхгүй /Үгүй/'
            WHEN MAX(CASE WHEN LOWER(c.SOLNAME) LIKE '%алба%' THEN 0 ELSE 1 END) = 1 THEN 'Газар, хэлтэс'
            ELSE 'Алба' END                                         AS VALUE_TEXT,
       COUNT(c.SOLNAME)                                             AS SOURCE_ROW_COUNT   -- өөрчлөгдсөн SOLID
FROM   (SELECT DISTINCT u1.BRANCHID FROM u1) b
LEFT   JOIN chg c ON c.BRANCHID = b.BRANCHID
GROUP  BY b.BRANCHID
