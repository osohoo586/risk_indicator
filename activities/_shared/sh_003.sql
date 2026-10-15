/*---
indicator_id: SH_003
name_mn: "Гарсан гомдлын тоо"
description: >
  Аудит орсноос хойшхи улирлын дундаж гомдол: ХҮГ-ын бүртгэлийн банк, ажилтны буруутай (IS_BANK_FAULT = Y)
  гомдол ÷ :p_quarters (аудитаас тайлант өдөр хүртэлх улирлын тоо). ДАГ-т ирж шалгагдсан гомдол байвал
  VALUE_TEXT = 'ДАГ-т гомдол ирж, шалгагдсан.' (шатлалын 5). SOL бүрийн VALUE-г үйл ажиллагаагаар нэмнэ.
  Ашигладаг: RI_01_0029, RI_02_0077, RI_03_0128, RI_04_0166, RI_06_0245, RI_07_0282, RI_08_0318, RI_09_0354, RI_10_0386, RI_11_0421, RI_13_0487, RI_15_0563 …
connection: oracle_whouse
frequency: quarterly
period: since_audit                # хэрэглэгч үзүүлэлтийн period_text хоосон бол энэ
rollup_metrics: {value: sum}      # SOL-уудын VALUE-г нэмнэ (тоо)
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score2"
scale_text: |
  0-Үнэлэхгүй /Гомдол гараагүй/
  2-ХҮГ-ын бүртгэлээр 2 хүртэл гомдол гарсан
  3-ХҮГ-ын бүртгэлээр 2-3 гомдол гарсан
  4-ХҮГ-ын бүртгэлээр 3-с дээш гомдол гарсан
  5-ДАГ-т гомдол ирж, шалгагдсан.
source_system: "ХҮГ, ДАГ"
required_info: |
  - ХҮГ-ийн гомдлын бүртгэл
  - ДАГ-ын гомдлын бүртгэл
method: |
  - Нийт гомдлоос банк болон ажилтны буруугаас шалтгаалж харилцагчид хүндрэл гарсан гомдлыг түүвэрлэнэ.
  - ДАГ-ын гомдлын бүртгэлийг түүвэрлэнэ.
  - Нийт гарсан гомдлын тоо/аудит орсноос хойш улирлын тоо.
period_text: "Аудит орсноос хойш хугацааны улирлын дундаж."
automatable: "Тийм"
data_mapping: "Салбар"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
test_dates: [2026-06-30, 2026-09-30]
---*/
WITH c AS (
    SELECT c.SOLID,
           SUM(CASE WHEN c.CHANNEL = 'ХҮГ' AND c.IS_BANK_FAULT = 'Y' THEN 1 ELSE 0 END)   AS CNT,
           MAX(CASE WHEN c.CHANNEL = 'ДАГ' AND c.STATUS = 'ШИЙДВЭРЛЭСЭН' THEN 1 ELSE 0 END) AS DAG
    FROM   {{schema.coremis}}.CUSTOMER_COMPLAINT c
    WHERE  c.REG_DATE >= :p_period_start
      AND  c.REG_DATE <  :p_report_date_next
    GROUP  BY c.SOLID
)
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(s.SOL_ID)                             AS ENTITY_ID,
       NVL(c.CNT, 0)                                 AS NUMERATOR,      -- хугацаанд гарсан гомдол
       NVL(c.CNT, 0) / :p_quarters                   AS VALUE,          -- улирлын дундаж
       CASE WHEN c.DAG = 1 THEN 'ДАГ-т гомдол ирж, шалгагдсан.' END AS VALUE_TEXT
FROM   {{schema.finacle}}.SOL s
LEFT   JOIN c ON c.SOLID = s.SOL_ID
