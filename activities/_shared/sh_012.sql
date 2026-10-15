/*---
indicator_id: SH_012
name_mn: "Дүрэм журам шинэчлэгдсэн эсэх"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй
  1-1 жил
  2-2 жил
  3-3 жил
  4-4 жил
  5-5 болон түүнээс дээш жил
source_system: "ЗахГ-УАА / Тухайн үйл ажиллагааг хариуцсан нэгж"
required_info: "- Тухайн үйл ажиллагаатай холбоотой дүрэм, журмын мэдээлэл"
method: "- Аудит орсноос хойш үйл ажиллагаатай холбоотой дүрэм, журам шинэчлэгдсэн эсэхийг баталгаажуулах"
period_text: "Дүрэм, журам шинэчлэгдсэн эсэх"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Үйл ажиллагааны дүрэм, журмаас хамгийн удаан шинэчлэгдээгүйн насжилт (жил): тайлант өдөр − MIN(LAST_REVISION_DATE),
  GRC.POLICY_DOCUMENT. Тайлант өдрөөс хойш шинэчилсэн журам (өмнөх огноо нь мэдэгдэхгүй) орохгүй.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(d.BRANCHID)                                          AS ENTITY_ID,
       (:p_report_date - MIN(d.LAST_REVISION_DATE)) / 365.25        AS VALUE,          -- жил
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{schema.grc}}.POLICY_DOCUMENT d
WHERE  d.APPROVED_DATE <= :p_report_date
  AND  d.LAST_REVISION_DATE <= :p_report_date
GROUP  BY d.BRANCHID
