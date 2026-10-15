/*---
indicator_id: RI_01_0020
name_mn: "Бүртгэлийн баримтад зөрчил илэрсэн эсэх /ХБГ-ХХХХ/"
status: REVIEW
version: 1.0.0
# ── Master ──
weight: 0.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-Гарын үсэггүй баримтаар гүйлгээ хийсэн эсвэл гүйлгээний баримтгүй, хяналтгүй
  4-Гарын үсэг зөрүүтэй баримтаар гүйлгээ хийсэн
  3-Гүйлгээ буруу хийсэн.
  2-Шимтгэл аваагүй, буруу авсан
  1-Зөрчилгүй
source_system: "СБМХ"
required_info: "Бүртгэлийн зөрчлийн мэдээлэл"
method: "ББГ-Архивлах байдлаар"
period_text: "Аудит орсноос хойш"
automatable: "Тийм"
# ── Тооцоолол ──
description: >
  Бүртгэлийн баримтын (архивын) шалгалтаар аудит орсноос хойш илэрсэн хамгийн ноцтой зөрчил
  (COREMIS.DOC_ARCHIVE_CHECK). VALUE_TEXT = мастерийн шатлалын текст (зөрчилгүй SOL → 'Зөрчилгүй'),
  VALUE = зөрчлийн тоо. Үйл ажиллагааны SOL-уудын хамгийн өндөр оноотой ангилал сонгогдоно.
connection: oracle_whouse
frequency: quarterly
rollup_metrics: {value: sum}
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH v AS (
    SELECT c.SOLID, c.VIOLATION_TEXT,
           ROW_NUMBER() OVER (PARTITION BY c.SOLID ORDER BY c.VIOLATION_LEVEL DESC, c.CHECK_DATE DESC) AS RN,
           COUNT(*) OVER (PARTITION BY c.SOLID)                     AS CNT
    FROM   {{schema.coremis}}.DOC_ARCHIVE_CHECK c
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
