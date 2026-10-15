/*---
indicator_id: SH_023
name_mn: "Банкны нууцын зэрэглэлтэй мэдээлэл задруулсан эсэх"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score4"
scale_text: |
  0-Үнэлэхгүй /Зөрчилгүй/
  4-Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан
  5-Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан зөрчил давтагдсан
source_system: "МАБХ, ДАГ-ын гомдлын бүртгэл"
required_info: |
  - МАБХ-ийн зөрчлийн мэдээлэл
  - ДАГ-т ирсэн гомдлын бүртгэлээс МАБ--тай холбоотой гомдлын мэдээлэл
method: "- Зөрчлийн мэдээллийг шүүж үйл ажиллагааг хариуцсан нэгжээс МАБ алдсан тохиолдол гарсан эсэхийг баталгаажуулна."
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Аудитаас хойш мэдээллийн нууц задруулсан тохиолдлын хамгийн ноцтой нь (GRC.INFOSEC_INCIDENT, DATA_TYPE =
  :p_data_type), гарсан SOL бүрээр. SH_024 (харилцагчийн нууц) нь энэ SQL-ийг sql_from + p_data_type-аар ашиглана.
connection: oracle_whouse
frequency: quarterly
params: {p_data_type: БАНК}
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH i AS (
    SELECT x.SOLID, MAX(x.SEVERITY) AS SEV, COUNT(*) AS CNT
    FROM   {{schema.grc}}.INFOSEC_INCIDENT x
    WHERE  x.DATA_TYPE = :p_data_type
      AND  x.INCIDENT_DATE >= :p_period_start
      AND  x.INCIDENT_DATE <  :p_report_date_next
    GROUP  BY x.SOLID
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(s.SOL_ID)                                            AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE WHEN i.SEV IS NULL THEN 'Үнэлэхгүй /Зөрчилгүй/'
            WHEN :p_data_type = 'БАНК' AND i.SEV >= 5 THEN 'Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан зөрчил давтагдсан'
            WHEN :p_data_type = 'БАНК' THEN 'Нууцын зэрэглэлтэй мэдээлэл, тухайн мэдээлэл агуулсан файлыг банкнаас гадагш гаргасан'
            WHEN i.SEV >= 5 THEN 'Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш гаргасан зөрчил давтагдсан'
            ELSE 'Харилцагчийн мэдээлэл, мэдээлэл агуулсан файлыг бусад руу и-мэйлээр илгээсэн, гадагш гаргасан' END AS VALUE_TEXT,
       NVL(i.CNT, 0)                                                AS SOURCE_ROW_COUNT
FROM   {{schema.finacle}}.SOL s
LEFT   JOIN i ON i.SOLID = s.SOL_ID
