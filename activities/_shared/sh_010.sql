/*---
indicator_id: SH_010
name_mn: "Action plan биелэлт"
status: REVIEW
version: 1.0.0
# ── Master ── (нийтлэг: 35 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  0-Үнэлэхгүй
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "СУГ-ТҮХ"
required_info: "Action plan-ийн хэрэгжилт"
method: "ИБГ-БХ-ийн Action plan-ын хэрэгжилтэд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Үгүй"
period: report                    # хамрах хугацаа
# ── Тооцоолол ── (master: гараар; demo DB-ээс автомат — ТААМАГ хүснэгт)
description: >
  Action plan-ы ажлуудаас тайлант хугацаанд хугацаа нь болсон (DUE_DATE) ажлын хэдэн хувь нь хугацаандаа
  шийдвэрлэгдсэн (RESOLVED_DATE ≤ DUE_DATE) — JIRA.ACTION_PLAN, BRANCHID бүрээр (ACTIVITY түвшин).
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'ACTIVITY'                                                   AS ENTITY_LEVEL,
       TO_CHAR(a.BRANCHID)                                          AS ENTITY_ID,
       SUM(CASE WHEN a.RESOLVED_DATE <= a.DUE_DATE THEN 1 ELSE 0 END) AS NUMERATOR,   -- хугацаандаа
       COUNT(*)                                                     AS DENOMINATOR,   -- хугацаа нь болсон
       SUM(CASE WHEN a.RESOLVED_DATE <= a.DUE_DATE THEN 1 ELSE 0 END) / COUNT(*) AS VALUE
FROM   {{schema.jira}}.ACTION_PLAN a
WHERE  a.DUE_DATE >= :p_period_start
  AND  a.DUE_DATE <= :p_report_date
GROUP  BY a.BRANCHID
