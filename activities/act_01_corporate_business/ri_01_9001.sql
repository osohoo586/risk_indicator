/*---
indicator_id: RI_01_9001
name_mn: АБХ-Дохиоллын түгшүүрийн зөрчил хураангуй
name_en: ABH alarm violation summary
description: >
  АБХ (Jira, ISSUETYPE = 11457) дохиоллын түгшүүрийн зөрчил бүр 1 мөр, тухайн хугацаанд
  бүртгэгдсэн (CREATED). Мөр бүрт дохиоллын компонентоор (COMP_ISSUE_CNT) болон
  салбар × компонентоор (BRANCH_COMP_ISSUE_CNT) тооцсон зөрчлийн тоо.
  Анхны SQL-ээс өөрчилсөн:
  1) J.CREATED-ээр хугацааг шүүнэ (анхных нь бүх түүхийг татдаг байсан → улирал бүр давтагдана).
  2) 'ABH-' || ISSUENUM баганад ISSUE_KEY нэр өгсөн.
  3) JIRA. → {{schema.jira}}.
  4) Master-д байхгүй нэмэлт үзүүлэлт (9001+): жин, шатлалгүй — оноонд орохгүй, мэдээллийн зорилготой.
     Хуучин RI_01_003 байсан (master 1/3 = Эх үүсвэрийн төлөвлөгөөний биелэлт тул солив).
  TODO: SALBAR_NEGJ_NER → SOL_ID холбоос олдвол ENTITY_LEVEL='SOL' болгоно (үйл ажиллагаагаар шүүгдэнэ).
connection: oracle_whouse          # TODO: JIRA schema аль Oracle-д байгааг баталгаажуулах
frequency: quarterly
status: IN_PROGRESS
version: 0.2.0
complexity: simple
rollup_metrics: {issue_cnt: sum}
score_metric: issue_cnt
test_dates: [2026-06-30, 2026-09-30]
empty_source: warn                 # тухайн улиралд зөрчил гараагүй байж болно (алдаа биш)
---*/
WITH BASE AS (
    SELECT A.DOHIOLOL_COMP,
           A.SALBAR_NEGJ_NER,
           J.ISSUENUM
    FROM   {{schema.jira}}.ABH_JIRA_NEW A
    JOIN   {{schema.jira}}.JIRAISSUE_NEW J
           ON A.ID = J.ID
    WHERE  J.ISSUETYPE = '11457'
      AND  J.CREATED >= :p_period_start
      AND  J.CREATED <  :p_report_date_next
)
SELECT 'UNIT'                                AS ENTITY_LEVEL,    -- салбар/нэгжийн нэрээр (SOL биш)
       NVL(SALBAR_NEGJ_NER, '(хоосон)')      AS ENTITY_ID,
       NVL(SALBAR_NEGJ_NER, '(хоосон)')      AS ENTITY_NAME,
       'issue_cnt'                           AS METRIC,
       COUNT(DISTINCT ISSUENUM)              AS VALUE,
       COUNT(*)                              AS SOURCE_ROW_COUNT
FROM   BASE
GROUP  BY SALBAR_NEGJ_NER
