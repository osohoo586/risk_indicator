/*---
indicator_id: SH_021
name_mn: "Зайны аудитаар зөрчил гарсан эсэх"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score3"
scale_text: |
  5-Зайны аудитаар зөрчил илэрч Илтгэх хуудас бичигдсэн
  4-Нэг төрлийн зөрчил давтагдан гарсан
  3-Нэг төрлийн зөрчил давтагдаагүй, өөр төрлийн зөрчил аудит дарааллан гарсан.
  2-Зайн аудитаар зөрчил гарсан боловч зөрчлийг арилгасан
  1-Зөрчил гараагүй.
source_system: "ЗАЧБХ"
required_info: "ЗАЧБХ-ийн зайны аудитын үр дүн"
method: "Зайны аудитын үр дүнд үндэслэн үнэлнэ."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойшхи зайны аудитын хамгийн ноцтой үр дүн (GRC.REMOTE_AUDIT_CHECK.RESULT_CODE 1 … 5).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(c.BRANCHID)                                          AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE MAX(c.RESULT_CODE)
            WHEN 5 THEN 'Зайны аудитаар зөрчил илэрч Илтгэх хуудас бичигдсэн'
            WHEN 4 THEN 'Нэг төрлийн зөрчил давтагдан гарсан'
            WHEN 3 THEN 'Нэг төрлийн зөрчил давтагдаагүй, өөр төрлийн зөрчил аудит дарааллан гарсан'
            WHEN 2 THEN 'Зайн аудитаар зөрчил гарсан боловч зөрчлийг арилгасан'
            ELSE 'Зөрчил гараагүй' END                              AS VALUE_TEXT,
       COUNT(*)                                                     AS SOURCE_ROW_COUNT
FROM   {{schema.grc}}.REMOTE_AUDIT_CHECK c
WHERE  c.CHECK_DATE >= :p_period_start
  AND  c.CHECK_DATE <  :p_report_date_next
GROUP  BY c.BRANCHID
