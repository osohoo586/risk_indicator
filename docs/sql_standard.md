# SQL-ийн стандарт

## 0. 1 тодорхойлолт = 1 файл

Ганц үйл ажиллагааны үзүүлэлт: `activities/act_GG_slug/ri_GG_NNNN.sql` (GG = бүлэг, NNNN = master-ийн №; нэмэлт
9001+). Олон үйл ажиллагаанд давтагддаг үзүүлэлт: НЭГ тодорхойлолт `activities/_shared/sh_NNN.sql`, үйл ажиллагаа
бүрийн `activity.yaml`-д `shared: - {id: RI_40_1545, def: SH_007, weight: 1.5}` ([dedup.md](dedup.md)).
Дээд хэсэг `/*--- … ---*/` нь YAML тохиргоо, доор нь SQL:

```sql
/*---
indicator_id: RI_40_1520
name_mn: "Банкны ажилтнуудын хүний нөөцийн эргэц"
status: REVIEW                    # TODO → IN_PROGRESS → REVIEW → TESTED → DONE
version: 1.0.0
# ── Master ── (ri.py import бичнэ — гараар засахгүй)
weight: 1.5                       # үйл ажиллагаа доторх жин (%)
score_type: "score1"
scale_text: |
  5-15-с дээш хувь
  4-13-14.9%
  …
period_text: "Сүүлийн 1 жил"      # → period: last_year (автоматаар)
# ── Тооцоолол ──
description: >
  Томьёо, нэгж, хуучин кодноос юу өөрчлөгдсөн.
connection: oracle_whouse
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
---*/
SELECT 'BANK' AS ENTITY_LEVEL, 'BANK' AS ENTITY_ID, … AS NUMERATOR, … AS DENOMINATOR, … AS VALUE
FROM   {{shared.erp.sol_flow}} f
```

indicator_id, үйл ажиллагаа, BRANCHID, SOLID-ууд, файлын нэр, оноо, жинг runner өөрөө бичнэ — SQL нь зөвхөн утгыг
тооцно.

## 1. Үр дүнгийн стандарт багана

| Багана | Заавал | Утга |
|---|---|---|
| `ENTITY_LEVEL` | ✔ | `SOL` (хамгийн түгээмэл), `ACTIVITY` (BRANCHID-аар), `BANK` (банк нийт), өөр (жнь `UNIT`) |
| `ENTITY_ID` | ✔ | SOL бол SOLID (`TO_CHAR(x.SOLID)`), ACTIVITY бол BRANCHID, BANK бол `'BANK'` |
| `VALUE` | ✔ | утга (NULL байж болно). Харьцаа бол 0.95 = 95% (шатлал хувиар бичигдсэн ч) |
| `NUMERATOR`, `DENOMINATOR` | | тоологч, хуваарь — **байвал үйл ажиллагааны утга = Σ тоологч / Σ хуваарь** |
| `VALUE_TEXT` | | ангиллын текст (шатлалын мөртэй яг ижил): `'ДАГ-т гомдол ирж, шалгагдсан.'`, `'Зөрчилгүй'` |
| `ENTITY_NAME`, `METRIC`, `SOURCE_ROW_COUNT`, `DATA_STATUS` | | нэр, олон хэмжигдэхүүн (`score_metric`), source-ийн мөр |

Өөр багана (жнь `BRANCH_ID`, `SCALE`) буцаавал `FAILED [OUTPUT_SCHEMA]`.

**SOL → үйл ажиллагаа:** runner тайлант өдрийн бүтцээр (`COREMIS.MAIN`, `shared/org/units.sql`) тухайн үйл
ажиллагааны SOLID-уудын мөрийг сонгож нэгтгэнэ. Тиймээс SQL нь **бүх SOL-ийг** гаргана, BRANCHID-аар шүүхгүй.

| Нэгтгэл | Хэзээ |
|---|---|
| Σ NUMERATOR / Σ DENOMINATOR | харьцаа, дундаж (эргэц, биелэлт, дундаж жил) — харьцааны дундаж БИШ |
| Σ VALUE | DENOMINATOR-гүй (тоо: гомдол, зөрчил) эсвэл `rollup_metrics: {value: sum}` |
| VALUE_TEXT | бүх SOL-ийн текстээс шатлалын хамгийн өндөр оноотой нь |

## 2. Горим

| Горим | Тохиргоо | Доор нь |
|---|---|---|
| Өөрийн SQL | `connection`, `frequency` | SELECT эсвэл procedure блок |
| Өөр файлын SQL | `sql_from: SH_031` + `params: {p_pkeys: "..."}` | юу ч бичихгүй |
| Нийтлэг тодорхойлолт (SQL) | `_shared/sh_NNN.sql`-д SQL; үйл ажиллагаанд `activity.yaml shared:` | SQL |
| Гараар | `manual: true` (ганц эсвэл нийтлэг тодорхойлолтод) | юу ч бичихгүй (`ri.py manual`) |

**Нийтлэг тодорхойлолт** (`activities/_shared/sh_NNN.sql`): 2+ үйл ажиллагаанд ижил нэртэй үзүүлэлт. SQL нь бүх
SOL (эсвэл BRANCHID)-ийн мөрийг НЭГ удаа гаргаж, үйл ажиллагаа бүр өөрийн SOL / BRANCHID-ийн мөрийг авна (35 үйл
ажиллагаа = 1 SQL). Хугацаа (аудитын огноо) өөр бол хугацаа бүрт нэг удаа. `activity.yaml`-ийн мөрд `params`
өгвөл тэр үйл ажиллагаанд тусдаа ажиллана; SQL нь `:p_activity_branch_id` ашиглавал үйл ажиллагаа бүрт.
ACTIVITY түвшний нийтлэг SQL бүх BRANCHID-ийн мөрийг (`{{shared.org.units}}`-аас) гаргана — мөргүй үйл ажиллагаа
"өгөгдөл алга".

**Procedure:** cursor-оор үр дүнгээ буцаадаг Oracle procedure-ийг шууд дуудна (стандарт баганатай cursor):

```sql
BEGIN
  {{schema.finacle}}.RA_LOAN_PKG.DECISION_SPEED(:p_period_start, :p_report_date, :rc);
END;
```

Procedure ч READ ONLY transaction дотор ажиллана — хүснэгтэд INSERT/UPDATE хийдэг procedure `SOURCE_WRITE_BLOCKED`.
Тийм бол логикийг SELECT болгоно.

**ClickHouse source:** `connection: clickhouse_dwh`, параметр `{p_report_date:Date}`, функц `countIf`, `toString` г.м.

**Өөр үзүүлэлтийн үр дүнгээс:** `connection: clickhouse_ra`, `{{schema.ri}}.ri_result`-аас уншина,
`dependencies: [RI_..]` заавал (жишээ: `activities/act_97_practice/ri_97_9006.sql`).

## 3. Параметр

| Oracle | ClickHouse | Утга |
|---|---|---|
| `:p_report_date` (`:p_date_to`) | `{p_report_date:Date}` | тайлант өдөр (хугацааны төгсгөл) |
| `:p_period_start` (`:p_date_from`) | `{p_period_start:Date}` | хугацааны эхлэл — `period`-оос |
| `:p_report_date_next` | `{p_report_date_next:Date}` | тайлант өдөр + 1 (цагтай багана: `< :p_report_date_next`) |
| `:p_prev_period_end` | | эхлэлээс өмнөх өдөр |
| `:p_quarters` | `{p_quarters:UInt32}` | [эхлэл, тайлант өдөр]-ийн улирлын тоо ("улирлын дундаж") |
| `:p_activity_branch_id` | | энэ үйл ажиллагааны BRANCHID (өөрийн SQL; нийтлэг SQL-д бол үйл ажиллагаа бүрт ажиллана) |
| `params: {p_x: утга}` | | файлын тохиргоо; орчин бүрт `config/<env>.yaml params:`-аар дарна |

**Хамрах хугацаа** (`period`, master-ийн "Хамрах хугацаа"-аас автоматаар, `period:`-аар дарж болно):

| period | :p_period_start | master |
|---|---|---|
| `report` | `-p 2026-Q3` → 07-01, `-d` → frequency-ийн эхлэл, `config/period.yaml` | Тайлант хугацаагаар |
| `last_year` | тайлант өдөр − 1 жил + 1 өдөр | Сүүлийн 1 жил |
| `since_audit` | тайлант өдрөөс өмнөх сүүлийн аудит (GRC, config `audit:`; эсвэл `LAST_AUDIT_DATE`), байхгүй бол сүүлийн 1 жил | Аудит орсноос хойш … |
| `latest` | (SQL нь `:p_report_date`-аас өмнөх сүүлийн үеийг өөрөө авна) | Сүүлийн үнэлгээгээр |

Хугацааны нөхцөл: `x.DATE_COL >= :p_period_start AND x.DATE_COL < :p_report_date_next`. Хатуу огноо бичихгүй.

## 4. shared/ — давхцах хэсэг

Хоёр ба түүнээс олон SQL-д ижил хэсэг байвал `shared/<систем>/<нэр>.sql`-д НЭГ удаа бичиж
`{{shared.<систем>.<нэр>}}`-ээр иш татна ([shared/README.md](../shared/README.md)):

```sql
FROM {{shared.erp.employee_sol}} e      -- тайлант өдөр ажиллаж буй ажилтан, SOLID, албан тушаал
FROM {{shared.erp.sol_flow}} f          -- SOL бүрийн HC_START, HC_END, SEPARATIONS
FROM {{shared.finacle.loan_book}} b     -- тайлант өдрийн зээлийн багц
FROM {{shared.org.units}} u             -- SOLID → BRANCHID
```

Баганын нэр (ERP, MAIN, FINACLE) өөр бол зөвхөн shared/-ийг засна — 300+ үзүүлэлт өөрөө засагдана.

## 5. Schema

`{{schema.coremis}}`, `{{schema.finacle}}`, `{{schema.erp}}`, `{{schema.cardzone}}`, `{{schema.main}}`,
`{{schema.jira}}`, `{{schema.ri}}` (үр дүн), `{{schema.cardzone_dwh}}` (ClickHouse) — орчин бүрийн бодит нэр
`config/<env>.yaml schemas:`-д.

## 6. Шалгалт (тохиргоонд)

```yaml
source_check: |                 # source-д тухайн өдрийн дата бэлэн эсэх (0 → SKIPPED SOURCE_NOT_READY)
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA WHERE REPORTNO = 'GL3003a' AND TXNDATE = :p_report_date
min_rows: 50                    # үүнээс цөөн мөр → VALIDATION_FAILED (source дутуу)
value_range: {min: 0, max: 1}   # SOL мөрийн VALUE хүрээнээс гарвал FAIL
max_change_pct: {pct: 30}       # үйл ажиллагааны утга өмнөх үеэс 30%+ өөрчлөгдвөл WARNING
empty_source: fail              # 0 мөр бол FAIL (default: WARNING, юу ч бичихгүй)
check_sql: |                    # бичсэний дараа ClickHouse дээр: CHECK_NAME, CHECK_STATUS, MESSAGE
  SELECT 'budget_positive' AS CHECK_NAME, if(sum(denominator) > 0, 'PASS', 'FAIL') AS CHECK_STATUS, '' AS MESSAGE
  FROM {target_table} WHERE indicator_id = {p_indicator_id:String} AND run_id = {p_run_id:String}
```

Runner үргэлж: давхардсан (ENTITY_LEVEL, ENTITY_ID, METRIC), хоосон ENTITY_ID, стандарт багана, буцааж уншиж тулгах.
prod-д шалгалт унавал бичихгүй (хуучин утга хэвээр), dev/local-д бичээд VALIDATION_FAILED.

## 7. Заавал (`python ri.py check`)

- `SELECT *`, `alias.*` хориглоно — баганыг нэрлэ.
- DML/DDL, `COMMIT`, `EXECUTE IMMEDIATE`, `DBMS_SQL`, `FOR UPDATE`, `LOCK TABLE`, ClickHouse `OPTIMIZE`, `SYSTEM …` хориглоно.
- Нууц үг, connection string, DB link (`@link`) хориглоно.
- Параметрийн бичиглэл connection-той таарна: Oracle `:p_x`, ClickHouse `{p_x:Type}`.
- Хатуу огноо (`DATE '2026-09-30'`) хориглоно.
- Procedure блок `:rc`-тэй байна.
- Иш татсан `{{shared.x}}` байх ёстой; хэн ч ашиглаагүй shared файл, ижил SQL-тэй хоёр файл → анхааруулга.
- `status: REVIEW`+ бол SQL-д TODO үлдээхгүй.
- Хуваах бүрт `NULLIF(x, 0)` / `nullIf(x, 0)`. Олон мөртэй хүснэгттэй JOIN хийгээд SUM хийвэл (fan-out) `EXISTS`.

## 8. Жишээ

| Файл | Юуг харуулна |
|---|---|
| `activities/_shared/sh_007.sql` | нийтлэг тодорхойлолт, SOL, Σ/Σ, `shared/erp/sol_flow.sql` |
| `activities/_shared/sh_003.sql` | тоо (Σ VALUE) + ангиллын текст (ДАГ → 5), `:p_quarters`, аудитаас хойш |
| `activities/_shared/sh_017.sql` … `sh_020.sql` | ACTIVITY түвшин (BRANCHID бүр), `{{shared.grc.last_audit}}`, "аудит ороогүй" |
| `activities/_shared/sh_011.sql` | MAIN-ийн хоёр snapshot-ийг харьцуулах (бүтцийн өөрчлөлт) |
| `activities/_shared/sh_023.sql`, `sh_024.sql` | нэг SQL + параметр (`sql_from` + `p_data_type`) |
| `activities/_shared/sh_029.sql` | BI тайлан, `source_check`, `check_sql`, `params` (PKEY нь config-оор) |
| `activities/_shared/sh_038.sql` | Oracle procedure (`:rc`) |
| `activities/act_40_human_resources/ri_40_1520.sql` | BANK түвшин, SH_007-той НЭГ shared код |
| `activities/act_40_human_resources/ri_40_1526.sql` | `:p_activity_branch_id`, `{{shared.org.units}}`, гараар шатлал (`scale:`) |
| `activities/act_01_corporate_business/ri_01_0020.sql` | ангиллын шатлал (`VALUE_TEXT` = хамгийн ноцтой зөрчил) |
| `activities/act_27_card_issuing/ri_27_9001.sql` | ClickHouse source |
| `activities/act_97_practice/` | дадлага: ERP, COREMIS + FINACLE, CARDZONE, өөр үзүүлэлтийн үр дүнгээс |
