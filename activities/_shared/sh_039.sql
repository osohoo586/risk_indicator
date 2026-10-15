/*---
indicator_id: SH_039
name_mn: "ЗХБ-ийн материал зөрчилтэй байх"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  5-Цохолттой олгосон материалын бүрдэл хугацаа хэтэрсэн.
  4-ЗХБ-н материалын бүрдэл дутуу /Гэрчилгээ, гэрээ/
  3-Эрх зүйн бичиг баримт алдаатай
  2-Програмд мэдээлэл бүртгээгүй /барьцаа, ХЗ/
  1-Зөрчилгүй
source_system: "ХБГ-ЗХБХ"
required_info: "Зээлийн хэрэг бүртгэлийн зөрчил"
method: "БПМГ-ын ЗХБХ-ийн ББГ-ыг хариуцсан ЗХБ-ийн ажилтнаас мэдээлэл авч үнэлнэ"
period_text: "Аудит орсноос хойш"
automatable: "Тийм"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
description: >
  Зээлийн хорооны (ЗХБ) материалын шалгалтаар аудит орсноос хойш илэрсэн хамгийн ноцтой зөрчил
  (COREMIS.LOAN_COMMITTEE_CHECK). VALUE_TEXT = мастерийн шатлалын текст, VALUE = зөрчлийн тоо.
connection: oracle_whouse
frequency: quarterly
rollup_metrics: {value: sum}
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH v AS (
    SELECT c.SOLID, c.VIOLATION_TEXT,
           ROW_NUMBER() OVER (PARTITION BY c.SOLID ORDER BY c.VIOLATION_LEVEL DESC, c.CHECK_DATE DESC) AS RN,
           COUNT(*) OVER (PARTITION BY c.SOLID)                     AS CNT
    FROM   {{schema.coremis}}.LOAN_COMMITTEE_CHECK c
    WHERE  c.CHECK_DATE >= :p_period_start
      AND  c.CHECK_DATE <  :p_report_date_next
      AND  c.VIOLATION_LEVEL > 1
)
SELECT 'SOL'                                                        AS ENTITY_LEVEL,
       TO_CHAR(s.SOL_ID)                                            AS ENTITY_ID,
       NVL(v.CNT, 0)                                                AS VALUE,          -- зөрчлийн тоо
       NVL(v.VIOLATION_TEXT, 'Зөрчилгүй')                           AS VALUE_TEXT      -- хамгийн ноцтой
FROM   {{schema.finacle}}.SOL s
LEFT   JOIN v ON v.SOLID = s.SOL_ID AND v.RN = 1
