---
description: Master-ийн мөрийг (эсвэл нэмэлт үзүүлэлтийг) хуучин procedure / SQL-ээс шинэ стандарт SQL болгож, local / dev дээр тестлэнэ
argument-hint: <Бүлэг> <№> [нэр] — дараа нь хуучин procedure эсвэл SQL-ээ paste хийнэ
---

Эрсдэлийн үзүүлэлтийн SQL бич. Хэрэглэгчийн өгсөн мэдээлэл:

$ARGUMENTS

Үр дүн нь ClickHouse-ийн `risk_assessment.ri_result`: үзүүлэлт × үйл ажиллагаа (BRANCHID) мөр + SOL задаргаа.
SQL нь зөвхөн утгыг тооцно; үйл ажиллагаа, BRANCHID, SOLID-ууд, оноо, жинг runner өөрөө. Дүрэм:
[docs/sql_standard.md](../../docs/sql_standard.md).

## Ажлын дараалал (заавал энэ дарааллаар)

1. **Файлыг олох.** `python ri.py status RI_GG_NNNN` хаана байгааг хэлнэ: олон үйл ажиллагаанд давтагддаг бол
   НЭГ тодорхойлолт `activities/_shared/sh_NNN.sql` (үйл ажиллагаа бүрийн `activity.yaml shared:`-д №, жин, зөрүү —
   [docs/dedup.md](../../docs/dedup.md)), ганц бол `activities/act_GG_*/ri_GG_NNNN.sql` (GG = бүлэг, NNNN = master-ийн
   №). `# ── Master ──` хэсгийг (нэр, жин, шатлал, хамрах хугацаа, аргачлал) уншиж томьёог ойлго — гараар засахгүй. Master-д байхгүй бол `python ri.py new -a ACT_GG --name-mn ... --name-en ...`
   (→ `ri_GG_9001.sql`, жингүй). Дутуу мэдээлэл (хуучин код, аль DB) байвал нэг асуултаар асуу, бусдыг таамаглахгүй.

2. **Давхардал шалгах.**
   - Нийтлэг тодорхойлолт (`sh_NNN.sql`) бол SQL-ийг ТЭНД нэг удаа бичнэ — бүх үйл ажиллагаанд тусна (SOL / BRANCHID
     бүрийн мөр гарга). Нэг үйл ажиллагаанд өөр параметр хэрэгтэй бол `activity.yaml`-ийн мөрд `params:`.
     `python ri.py duplicates` — нийтлэг тодорхойлолтын жагсаалт (SQL / гарын).
   - `ls -R shared/` — хэрэгтэй хэсэг (`{{shared.erp.employee_sol}}`, `{{shared.erp.sol_flow}}`,
     `{{shared.finacle.loan_book}}`, `{{shared.org.units}}`) байвал дахин бичихгүй, иш тат. Шинэ давхцах хэсэг
     гарвал `shared/<систем>/<нэр>.sql`-д гарга ([shared/README.md](../../shared/README.md)).
   - Зөвхөн параметр (тайлангийн мөр, сегмент, бүс) өөр бол `sql_from: SH_NNN` (эсвэл `RI_GG_NNNN`) +
     `params: {p_xxx: ...}` — жишээ SH_024 = SH_023-ийн SQL + `p_data_type`.

3. **SQL бичих** (`---*/`-ийн доор, `manual: true`-г хас):
   - Стандарт багана: `ENTITY_LEVEL, ENTITY_ID, VALUE` (+ `NUMERATOR, DENOMINATOR` харьцаа бол, `VALUE_TEXT` ангилал
     бол — шатлалын мөрийн текстийг яг адил). SOL түвшинд БҮХ SOL-ийг гарга (`TO_CHAR(x.SOLID) AS ENTITY_ID`) — runner
     үйл ажиллагааны SOL-уудаар Σ тоологч / Σ хуваарь. Банк нийт бол `'BANK'`.
   - Харьцааг 0–1-ээр (0.95 = 95%), шатлал хувиар бичигдсэн ч.
   - Хугацаа: `x.DATE_COL >= :p_period_start AND x.DATE_COL < :p_report_date_next` (master-ийн "Хамрах хугацаа"
     автоматаар `period` болно). Тоо / улирлын дундаж бол `/ :p_quarters`. Хатуу огноо бичихгүй.
   - Schema: `{{schema.coremis}}`, `{{schema.finacle}}`, `{{schema.erp}}`, `{{schema.cardzone}}`, `{{schema.main}}`.
   - Хуучин procedure cursor буцаадаг бол шууд дуудаж болно: `BEGIN {{schema.x}}.PKG.PROC(:p_period_start,
     :p_report_date, :rc); END;` — cursor нь стандарт баганатай байх ёстой. Хүснэгтэд INSERT хийдэг procedure READ ONLY
     transaction-д `SOURCE_WRITE_BLOCKED` болно → логикийг SELECT болго.
   - Python / pandas-ын merge, fillna, groupby-г JOIN, NVL, GROUP BY болго. Хуваах бүрт `NULLIF(x, 0)`; олон мөртэй
     хүснэгттэй JOIN хийгээд SUM хийвэл (fan-out) `EXISTS`.
   - `SELECT *`, INSERT/UPDATE/DELETE/COMMIT бичихгүй. Параметр: Oracle `:p_x`, ClickHouse `{p_x:Date}`.
   - Хуучин кодноос өөрчилсөн бүх зүйлийг тохиргооны `description`-д дугаарлаж жагсаа.

4. **Тохиргоо** (`# ── Тооцоолол ──` хэсэгт): `description`, `connection` (oracle_whouse / clickhouse_dwh /
   clickhouse_ra), `frequency`, `status: IN_PROGRESS`, `test_dates`, зөвлөмж `source_check` (source бэлэн эсэх),
   `min_rows`, `value_range`, `max_change_pct`. Орчин бүрт өөр параметр (жнь PKEY) бол файлд `params: {p_x: TODO}`,
   утгыг `config/<env>.yaml params:`-д. Шатлал задрахгүй (`check`-ийн WARN) бол `scale: {type: numeric, numericRules: [...]}`.

5. **Тест**:
   ```bash
   .venv/bin/python ri.py check activities/act_GG_*/ri_GG_NNNN.sql --env local
   .venv/bin/python ri.py test RI_GG_NNNN --env local          # demo DB байвал; бодит дата дээр --env dev
   .venv/bin/python ri.py verify --env dev activities/act_GG_*/ri_GG_NNNN.sql -d <test_date>
   ```
   Нийтлэг тодорхойлолт бол: `ri.py run --env dev activities/_shared/sh_NNN.sql -p 2026-Q3` (бүх үйл ажиллагаа).
   Холболтын асуудал бол `ri.py doctor --env dev`. DB-д холбогдож чадахгүй бол зогсоод хэрэглэгчид хэл
   (нууц үг асуухгүй, `.env`-ийг уншихгүй).

6. **Тайлан**: үүссэн / өөрчилсөн файлууд (shared/, calc бол түүнийг ашигладаг үзүүлэлтүүд), тестийн үр дүн
   (SUCCESS / WARNING / алдаа), 2–3 SOL болон үйл ажиллагааны утга, оноо, хуучин кодноос өөрчилсөн логик, хэрэглэгч
   баталгаажуулах зүйл (баганын нэр, PKEY). Дараагийн алхам: хуучин тайлантай тулгах →
   `python ri.py status RI_GG_NNNN REVIEW --env dev` → commit → MR. Commit, push хийхгүй.
