/*---
indicator_id: SH_017
name_mn: "Өмнөх аудитаас хойшхи хугацаа"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score3"
scale_text: |
  1-0-1 жил
  2-1-2 жил
  3-2-2.5 жил
  4-2.5-3 жил
  5-3 ба түүнээс дээш жил, аудит ороогүй
source_system: "ДАГ, Auditsolution"
required_info: "- Өмнөх аудитын огноо"
method: "- Аудит орсноос хойш хугацааг тодорхойлно."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Сүүлийн дотоод аудитаас (shared/grc/last_audit.sql) тайлант өдөр хүртэлх хугацаа (жил). Аудит ороогүй →
  VALUE_TEXT 'аудит ороогүй' (шатлалын 5).
connection: oracle_whouse
frequency: quarterly
period: latest                     # master-ийнхыг дарна: сүүлийн аудитыг өөрөө үнэлнэ — аудит бүрт дахин ажиллуулахгүй
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       (:p_report_date - la.LAST_AUDIT_DATE) / 365.25               AS VALUE,          -- жил
       CASE WHEN la.LAST_AUDIT_DATE IS NULL THEN 'аудит ороогүй' END AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN {{shared.grc.last_audit}} la ON la.BRANCHID = b.BRANCHID
