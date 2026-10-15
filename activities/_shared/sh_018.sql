/*---
indicator_id: SH_018
name_mn: "Өмнөх аудитын үнэлгээ"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score3"
scale_text: |
  0-Үнэлэхгүй /Өмнө аудит хийж байгаагүй/
  1-Хангалттай
  3-Сайжрулах шаардлагатай
  5-Хангалтгүй
source_system: "ДАГ, Auditsolution"
required_info: "- Өмнөх аудитын үнэлгээ"
method: |
  - Өмнөх аудитын үнэлгээ.
  Идэвхитэй менежмент хэрэгтэй - Хангалтгүй
  Байнгын хяналт шаардлагатай - Сайжруулах шаардлагатай
  Тодорхой давтамжтай мониторинг хэрэгтэй - Сайжруулах шаардлагатай
  Анхаарал татах асуудал байхгүй. - Хангалттай.
period_text: "Аудит орсноос хойш хугацаанд"
period: since_audit                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Сүүлийн дотоод аудитын үнэлгээ (RATING_CODE 1 Хангалттай, 3 Сайжруулах шаардлагатай, 5 Хангалтгүй).
connection: oracle_whouse
frequency: quarterly
period: latest                     # master-ийнхыг дарна: сүүлийн аудитыг өөрөө үнэлнэ
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(b.BRANCHID)                                          AS ENTITY_ID,
       NULL                                                         AS VALUE,
       CASE la.RATING_CODE WHEN 1 THEN 'Хангалттай' WHEN 3 THEN 'Сайжрулах шаардлагатай' WHEN 5 THEN 'Хангалтгүй'
                           ELSE 'Үнэлэхгүй /Өмнө аудит хийж байгаагүй/' END AS VALUE_TEXT
FROM   (SELECT DISTINCT u.BRANCHID FROM {{shared.org.units}} u) b
LEFT   JOIN {{shared.grc.last_audit}} la ON la.BRANCHID = b.BRANCHID
