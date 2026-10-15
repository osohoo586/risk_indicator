/*---
indicator_id: SH_029
name_mn: "Зээлийн төлөвлөгөөний биелэлт"
status: REVIEW
version: 0.4.0
# ── Master ── (нийтлэг: 2 үйл ажиллагаа; зөрүүтэйг activity.yaml-ийн shared:-д)
score_type: "score1"
scale_text: |
  1-96.1%-аас дээш
  3-90.1%-96%
  5-90% - с доош
source_system: "BI тайлангийн систем"
required_info: "Балансын төлөвлөгөөний биелэлт"
method: "Төлөвлөгөөний биелэлтийн хувьд үндэслэн үнэлнэ."
period_text: "Тайлант хугацаагаар"
automatable: "Тийм"
period: report                 # хамрах хугацаа → :p_period_start (report / last_year / since_audit / latest)
# ── Тооцоолол ──
name_en: Loan plan fulfillment
description: >
  Салбар бүрээр зээлийн төлөвлөгөөний биелэлт.
  FULFILLMENT_RATIO = SUM(BALANCE) / SUM(BUDGET)  (0.95 = 95% биелсэн).
  Эх сурвалж: coremis.GL_REPORT_DATA, REPORTNO = 'GL3003a', хасах PKEY-ээс бусад бүх мөр.
  Хуучин FNB1041-ээс (load_fnb1041) ялгаа:
  1) Биелэлт = BALANCE / BUDGET (хуучин нь (BALANCE - BUDGET) / BUDGET).
  2) GL_USER_BRANCH-ийг JOIN биш EXISTS-ээр шүүнэ (хуучин JOIN дүнг давхар тоолж болох байсан).
  3) Дүн төгрөгөөр (хуучин нь /1000). 4) Огноо зөвхөн тайлант өдөр (хуучин нь ±4 хоног хайдаг).
connection: oracle_whouse
frequency: quarterly              # улиралд 1 удаа
# SQL нь SOL бүрийн NUMERATOR (гүйцэтгэл), DENOMINATOR (төлөвлөгөө)-ийг гаргана. Runner үйл ажиллагааны
# SOL-уудаар Σгүйцэтгэл / Σтөлөвлөгөө тооцоод шатлалаар оноо өгнө (0.95 → 95% → 3).
test_dates: [2026-06-30, 2026-09-30]
legacy: {table: RISKASSESSMENT.FNB1041, loader: load_fnb1041}
# Source-д тухайн өдрийн GL3003a мэдээ ачаалагдаагүй бол ажиллахгүй (SKIPPED: SOURCE_NOT_READY)
source_check: |
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA
  WHERE REPORTNO = 'GL3003a' AND TXNDATE = :p_report_date
# Үйл ажиллагааны биелэлт өмнөх үеэс 30%-иас их өөрчлөгдвөл WARNING
max_change_pct: {pct: 30}
# Балансын төлөвлөгөөний (GL3003a) ЭХ SQL — RI_01_0003, RI_01_0007 нь sql_from-оор ашиглана.
# p_pkeys: тооцох PKEY-ууд таслалаар ("10001,10002"). Хоосон бол хасагдаагүй БҮХ PKEY (хуучин FNB1041).
# Орчин бүрт config/<env>.yaml params-аар (local demo: 10001,10002). "TODO" бол ажиллахгүй.
params: {p_pkeys: "TODO"}
# min_rows: 100                   # салбарын тоо тогтоод тавина (дутуу ирвэл FAIL)
check_sql: |
  SELECT 'plan_ratio' AS CHECK_NAME,
         if(countIf(result_number IS NULL OR result_number < 0) = 0, 'PASS', 'FAIL') AS CHECK_STATUS,
         concat('Биелэлт: ', toString(any(result_number)), ' (NULL = төлөвлөгөө 0 / алга)') AS MESSAGE
  FROM {target_table}
  WHERE risk_ind_id = {p_indicator_id:String} AND snapshot_date = {p_report_date:Date}
    AND run_id = {p_run_id:String}
---*/
WITH gl AS (
    SELECT g.BRANCH                         AS branch,
           SUM(g.BUDGET)                    AS budget_amt,
           SUM(g.BALANCE)                   AS balance_amt,
           COUNT(*)                         AS source_row_count
    FROM   {{schema.coremis}}.GL_REPORT_DATA g
    WHERE  g.REPORTNO = 'GL3003a'
      AND  g.TXNDATE  = :p_report_date
      AND  g.BRANCH IS NOT NULL
      AND  g.PKEY NOT IN (                  -- Хуучин _EXCL_FNB1041 жагсаалт
               25430, 25432, 25433, 25434, 25435, 25436, 25437, 25438, 25439, 25440,
               25441, 25442, 25443, 25445, 25446, 25447, 25448, 25449, 25450, 25451,
               25452, 25453, 25454, 25455, 25456, 25487,
               26331, 26332, 26333, 26334, 26335, 26336, 26337, 26338, 26339, 26340,
               26341, 26342
           )
      AND  (COALESCE(LENGTH(:p_pkeys), 0) = 0
            OR INSTR(',' || :p_pkeys || ',', ',' || g.PKEY || ',') > 0)
      AND  EXISTS (SELECT 1
                   FROM   {{schema.coremis}}.GL_USER_BRANCH ub
                   WHERE  ub.SUB_BRANCH = g.BRANCH)
    GROUP  BY g.BRANCH
)
SELECT 'SOL'                                            AS ENTITY_LEVEL,
       TO_CHAR(s.SOL_ID)                                AS ENTITY_ID,
       s.SOL_DESC                                       AS ENTITY_NAME,
       gl.balance_amt                                   AS NUMERATOR,      -- гүйцэтгэл
       gl.budget_amt                                    AS DENOMINATOR,    -- төлөвлөгөө
       gl.balance_amt / NULLIF(gl.budget_amt, 0)        AS VALUE,          -- биелэлт (0.95 = 95%)
       gl.source_row_count                              AS SOURCE_ROW_COUNT
FROM   gl
JOIN   {{schema.finacle}}.SOL s
       ON s.SOL_ID = gl.branch
