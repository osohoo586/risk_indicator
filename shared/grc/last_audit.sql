-- Тайлант өдрөөс өмнөх СҮҮЛИЙН дотоод аудит (GRC.AUDIT_ENGAGEMENT, END_DATE = тайлан гарсан өдөр), BRANCHID бүрээр.
-- Ашигладаг: SH_017 … SH_020 (аудитын үзүүлэлт), runner (config audit: — "аудит орсноос хойш" хугацааны эхлэл).
-- Буцаах: BRANCHID, ENGAGEMENT_ID, LAST_AUDIT_DATE, RATING_CODE
SELECT a.BRANCHID              AS BRANCHID,
       a.ENGAGEMENT_ID         AS ENGAGEMENT_ID,
       a.END_DATE              AS LAST_AUDIT_DATE,
       a.RATING_CODE           AS RATING_CODE
FROM   (SELECT e.BRANCHID, e.ENGAGEMENT_ID, e.END_DATE, e.RATING_CODE,
               ROW_NUMBER() OVER (PARTITION BY e.BRANCHID ORDER BY e.END_DATE DESC, e.ENGAGEMENT_ID DESC) AS RN
        FROM   {{schema.grc}}.AUDIT_ENGAGEMENT e
        WHERE  e.END_DATE <= :p_report_date) a
WHERE  a.RN = 1
