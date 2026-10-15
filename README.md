# Risk Indicators (RA) — эрсдэлийн үнэлгээний үзүүлэлт

master.xlsx-ийн **35 үйл ажиллагаа, 1,380 үзүүлэлт**-ийг тооцоолж ClickHouse-ийн `risk_assessment.ri_result`-д
бичнэ. Source (Oracle: COREMIS, FINACLE, ERP, CARDZONE …, ClickHouse DWH)-ийг **зөвхөн уншина**.

| Ойлголт | Утга |
|---|---|
| **SOLID** | хамгийн жижиг нэгж: хэлтэс, алба, салбар. SQL бүр энэ түвшинд тоолно |
| **BRANCHID** | SOLID-уудыг нэгтгэсэн нэгж; **үйл ажиллагаа бүр нэг BRANCHID** (`config/activity_map.csv`) |
| **Үйл ажиллагаа (activity)** | master-ийн бүлэг = үнэлгээ (`activities/act_GG_*`). Нийт оноо = Σ(жин × оноо) / Σ(оноотой жин) |
| **Үзүүлэлт (indicator)** | master-ийн мөр = `RI_GG_NNNN` (GG = бүлэг, NNNN = master-ийн №) |
| **Тодорхойлолт** | давхардалгүй үзүүлэлт: 1,380 мөр → **498**. Олон үйл ажиллагаанд давтагддаг 50 нь `activities/_shared/sh_NNN.sql` (нэг SQL / аргачлал / шатлал), ганц үйл ажиллагааных 448 нь өөрийн `ri_GG_NNNN.sql` |

SOLID → BRANCHID-ийг тайлант өдрөөр `COREMIS.MAIN`-аас (`shared/org/units.sql`) уншина — бүтэц өөрчлөгдвөл
кодыг засахгүйгээр автоматаар тусна.

```
master.xlsx ──ri.py import──► activities/_shared/sh_NNN.sql       (50 нийтлэг тодорхойлолт → 932 үзүүлэлт)
  (давхардлыг нэгтгэнэ:       activities/act_GG_*/activity.yaml   (shared: №, тодорхойлолт, жин, зөрүү)
   ri.py dedup)               activities/act_GG_*/ri_GG_NNNN.sql  (448 ганц үйл ажиллагааны үзүүлэлт)
                              shared/{org,erp,finacle,grc}/*.sql  (SQL-д давхцдаг хэсэг)
                                      │
     Oracle / ClickHouse source ◄─────┤ ri.py run / auto  (READ ONLY)
                                      ▼
              SOL мөрүүд ──► үйл ажиллагааны SOL-уудаар Σ тоологч / Σ хуваарь ──► шатлал → оноо 1–5
                                      ▼
     ClickHouse risk_assessment.ri_result  (бичээд буцааж уншиж мөр бүрээр тулгана)
        INDICATOR × ACTIVITY мөр + SOL задаргаа · ACTIVITY нийт оноо, түвшин · audit · history
        view: v_risk_indicators, v_activity_score, v_indicator_score, v_indicator_detail
```

## 1. Эхлэх

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
git config core.hooksPath .githooks            # commit бүрт python3 ri.py check
cp .env.example .env                           # dev / test / prod-ийн нууц үг (git-д орохгүй)
python ri.py doctor --env dev                  # сан, холболт, ClickHouse эрх
```

**Local (Docker Oracle + ClickHouse, стандарт банкны demo DB)** — prod-той ижил бүтэц, нууц үг хэрэггүй:

```bash
./tests/local/setup.sh                         # container, demo DB (COREMIS, FINACLE, ERP, CARDZONE, JIRA), init-db
python tests/local/demo_check.py               # бүтэн урсгал + эталонтой тулгах → output/demo_report.html
./tests/local/demo.sh --step                   # алхам алхмаар тайлбартай
```

## 2. Ажиллуулах

```bash
python ri.py run    --env dev activities/act_40_human_resources/ -p 2026-Q3   # folder
python ri.py run    --env dev activities/act_40_human_resources/ri_40_1520.sql -d 2026-09-30   # нэг файл
python ri.py run    --env dev activities/_shared/sh_007.sql -p 2026-Q3        # тооцооллыг ашигладаг 35 үзүүлэлт
python ri.py run    --env dev --all -p 2026-Q2 -p 2026-Q3                       # бүгд, 2 улирал
python ri.py verify --env dev activities/act_40_human_resources/ -p 2026-Q3   # source ↔ ClickHouse (бичихгүй)
python ri.py auto   --env prod --all --plan                                     # дутуу / хуучирсныг л (prod DAG)
python ri.py manual template -a 1006 -d 2026-09-30                              # гарын үнэлгээний Excel
python ri.py manual load output/manual/manual_1006_20260930.xlsx --env dev
python ri.py report --env dev -a 1006 -d 2026-09-30                             # үйл ажиллагааны HTML тайлан
```

Дэлгэрэнгүй, хүлээгдэх гаралт: [run.md](run.md).

## 3. Бүтэц

```
activities/
  _shared/sh_NNN.sql              олон үйл ажиллагааны НЭГ тодорхойлолт (нэр, аргачлал, шатлал + SQL эсвэл manual)
  act_01_corporate_business/      activity.yaml (нэр, owner, defaults, shared: — нийтлэг тодорхойлолтын мөрүүд)
                                  + ri_01_NNNN.sql (зөвхөн энэ үйл ажиллагааны үзүүлэлт)
  …  act_40_human_resources/
  act_97_practice/                дадлага (example: true — --all-д орохгүй)
shared/                           SQL-ийн давхцах хэсэг: org/units, erp/employee_sol, erp/sol_flow, finacle/loan_book,
                                  grc/last_audit
config/                           local / dev / test / prod.yaml, activity_map.csv (бүлэг → BRANCHID, аудитын огноо),
                                  activity_units.csv (MAIN-гүй үеийн SOLID → BRANCHID), scoring.yaml, period.yaml
ddl/clickhouse/                   ri_result, ri_execution_audit, ri_history, ri_activity, ri_indicator, views
ri_runner/                        runner (metadata, runner, store, db, scale, checks, verify, auto, manual, report …)
tests/unit/                       DB-гүй тест (pytest)
tests/local/                      Docker demo: bank_demo.py (DB), seed_bank.py, bank_golden.py (эталон), demo_check.py
deploy/airflow_dag.py             prod: өдөр бүр ri.py auto --env prod --all
docs/                             sql_standard.md, onboarding.md, examples.md, workflow.md, ui_tables.md
```

## 4. Үзүүлэлтийн горим

| Горим | Хаана | Тоо | Тооцоолол |
|---|---|---|---|
| **shared** | `activity.yaml shared: {id, def: SH_007, weight}`, SQL нь `_shared/sh_007.sql` | 762 | нийтлэг SQL НЭГ удаа → үйл ажиллагаа бүр өөрийн SOL / BRANCHID-аар |
| **sql** | өөрийн `ri_GG_NNNN.sql` (эсвэл `sql_from` + `params`) | 9 + 2 нэмэлт | энэ үзүүлэлтэд л |
| **manual** | `manual: true` (өөрийн файл эсвэл SQL-гүй нийтлэг тодорхойлолт) | 609 | хүн Excel-ээр (`ri.py manual`) |

**Давхардал:** ижил нэр = нэг тодорхойлолт. Үйл ажиллагаа бүрийн зөрүүг ([`ri.py dedup`](docs/dedup.md) тайлан)
дүрмээр шийдсэн: master-т эвдэрсэн хуулбар шатлал ("s-Дунд", шилжсэн багана, илүү мөр) → нийтлэг шатлал;
санаатай өөр шатлал, хугацаа, аргачлал → тухайн үйл ажиллагаанд дарна (`activity.yaml`); SQL байвал бүгд автомат.
master-д "Автоматжуулах: Үгүй" байсан 14 нийтлэг тодорхойлолтыг системээс (GRC аудит, ERP, JIRA, MAIN) тооцох
SQL-тэй болгосон (demo, ТААМАГ хүснэгт) — 1,380-аас 771 нь автомат.

**Хамрах хугацаа** (`period`) master-ийн "Хамрах хугацаа"-аас автоматаар: `report` (тайлант хугацаа),
`last_year` (сүүлийн 1 жил), `since_audit` (үйл ажиллагааны сүүлийн аудитаас — GRC-ийн аудитын бүртгэлээс тайлант
өдрөөр, config `audit:`; эсвэл `activity_map.csv LAST_AUDIT_DATE`),
`latest` (сүүлийн үнэлгээ). SQL-д `:p_period_start` … `:p_report_date`, `:p_quarters` (улирлын тоо).

**Оноо:** master-ийн шатлалын текстийг (`scale_text`) parser нь `{numericRules, stringRules}` болгоно
(хувь/харьцааг автоматаар тулгана, ангиллын текст `VALUE_TEXT`-ээр). Задрахгүй бол `scale:`-ийг гараар.

## 5. Баталгаа

- **Source зөвхөн уншина:** Oracle query бүр `SET TRANSACTION READ ONLY` (procedure дотор ч UPDATE → ORA-01456 →
  `SOURCE_WRITE_BLOCKED`), ClickHouse source `readonly=2`. `ri.py check` DML/DDL, `EXECUTE IMMEDIATE`, `FOR UPDATE`-ийг хориглоно.
- **Бичсэнээ буцааж тулгана:** insert бүрийн дараа мөр бүрийг ClickHouse-оос уншиж тулгана; зөрвөл бичсэнээ
  устгаж `FAILED [INSERT_MISMATCH]` — хуучин утга хэвээр. SUCCESS = ClickHouse-д яг тооцсоноор бичигдсэн.
- **Давхардахгүй:** дахин ажиллуулахад шинэ мөр бичигдэж, хуучин нь `ri_history`-д шилжинэ.
- **Нэг алдаа бусдыг зогсоохгүй:** timeout, dependency тойрог, source бэлэн биш (`source_check`), стандарт багана дутуу,
  давхардсан мөр — тухайн үзүүлэлт л алгасагдана/унана, audit-д код, шалтгаантай.
- **verify:** source дээр дахин тооцоолж ClickHouse-тэй мөр бүрээр, үйл ажиллагааны нийт оноог үзүүлэлтүүдээс нь.
- **auto:** ШИНЭ / АЛДАА / ӨӨРЧЛӨГДСӨН (SQL, нийтлэг тооцоолол, shared, params) / ХАМААРАЛ-ыг л ажиллуулна.

- **Хурд:** run-ий турш thread бүрт DB холболтыг дахин ашиглана; хуучин мөрийг тайлант өдөр бүрт НЭГ DELETE-ээр
  (dependency-тэй бол түүнээс өмнө) — 1,546 үзүүлэлт × өдөр ~8 сек.

Demo DB дээрх бүтэн шалгалт (`tests/local/demo_check.py`): эталон (Python, SQL-ээс үл хамааран) 2,764/2,764,
тодорхойлолт бүр 500/500, үйл ажиллагааны нийт оноо 70/70, хамгаалалт ба алдааны тохиолдол 20/20 —
[docs/examples.md](docs/examples.md). Үзүүлэлт бүрийн static тест: `pytest tests/unit/test_catalog.py`.

## 6. Шинэ үзүүлэлт нэмэх

Claude Code-д: `/new-indicator 40 1525 Албан тушаалд сонгон шалгаруулалтын дундаж хугацаа` → хуучин SQL / procedure-оо paste.
Гараар: [docs/onboarding.md](docs/onboarding.md), SQL-ийн дүрэм: [docs/sql_standard.md](docs/sql_standard.md).

```bash
python ri.py status RI_40_1545                # хаана байна: activity.yaml-ийн мөр → тодорхойлолт SH_007
python ri.py test RI_40_1520 --env dev       # check → dry-run → test_dates run → show (SH_007 бол бүх үйл ажиллагаа)
python ri.py status RI_40_1520 REVIEW --env dev   # нийтлэг бол: status SH_007 REVIEW
```

## 7. Командууд

| Команд | Юу хийдэг |
|---|---|
| `check [зам] [--env]` | Static шалгалт (DB-гүй): metadata, SQL дүрэм, dialect, shared/, жин, шатлал, BRANCHID |
| `run <зам\|-i\|-a\|--all> -p/-d/--from --to` | Ажиллуулж ClickHouse-д бичнэ (`--dry-run`, `--save-csv`, `--workers`) |
| `verify` | Дахин тооцоолж ClickHouse-тэй тулгана (бичихгүй), зөрвөл exit 1 |
| `auto [--plan] [--as-of] [--since]` | Дутуу / хуучирсныг л ажиллуулна |
| `retry --run-id` | Тухайн run-ий амжилтгүйг ижил хугацаагаар |
| `manual template / load` | Гарын үнэлгээ (Excel) |
| `aggregate -a -d` | Үйл ажиллагааны нийт оноог дахин тооцох |
| `show -i / -a -d` | ri_result-ийг харах (SOL задаргаатай) |
| `report -a -d [--open]` | Үйл ажиллагааны HTML тайлан |
| `import master.xlsx [--dry-run] [--update]` | Master-аас activities/ (давхардалгүй); `--update` — master хэсгийг шинэчилж, давтагдсан нэрийг нийтлэг тодорхойлолт болгоно |
| `dedup master.xlsx [--open]` | Давхардлыг хэрхэн шийдсэн HTML тайлан (зөрүү, гэр бүл, төстэй нэр) |
| `status <ID> [ТӨЛӨВ]` | Төлөвгүй: үзүүлэлт / тодорхойлолт хаана байгаа, горим; төлөвтэй: шалгаад төлөв солих |
| `duplicates`, `progress`, `new`, `new-activity`, `test`, `doctor`, `init-db`, `clean` | Туслах |

## 8. Орчин

| Орчин | Source | Үр дүн | min_status |
|---|---|---|---|
| local | Docker Oracle (demo DB) + ClickHouse `cardzone_dwh` | `risk_assessment_local` | TODO |
| dev | `.env`-ийн DEV_* | `risk_assessment` | TODO |
| test | TEST_* | `risk_assessment` | REVIEW |
| prod | PROD_* | `risk_assessment` | TESTED (`insert_on_validation_fail: false`, clean хориотой) |

Орчин бүрт өөр параметр (жнь BI тайлангийн PKEY): `config/<env>.yaml` → `params: {SH_029: {p_pkeys: "..."}}`
(нийтлэг тодорхойлолтод — бүх үйл ажиллагаанд) эсвэл `RI_01_0005: {…}` (ганц үзүүлэлтэд).

## 9. Тодруулах зүйлс

- **BRANCHID алга** (`config/activity_map.csv` CONFIDENCE = ТОДРУУЛАХ): бүлэг 2, 10, 11, 20, 21 — бичих хүртэл үр
  дүн хадгалагдахгүй (`BRANCH_NOT_MAPPED`). BRANCHID 2001 (бүлэг 8)-д `activity_units.csv`-д SOL алга.
- **ТААМАГ баганын нэр:** ERP, MAIN, FINACLE-ийн багана — бодит нэр өөр бол зөвхөн `shared/*.sql`, `activities/_shared/*`-ийг засна.
- **PKEY:** SH_029 … SH_033, RI_01_0005, RI_01_0014-ийн BI тайлангийн мөрүүд (`params: {p_pkeys: TODO}`) —
  `config/<env>.yaml params` (local-д demo утга бий).
- **Аудитын огноо:** `config/<env>.yaml audit:` (GRC-ийн бодит хүснэгт) идэвхжүүлэх хүртэл
  `activity_map.csv LAST_AUDIT_DATE`; хоёулаа хоосон бол "аудитаас хойш" нь сүүлийн 1 жил болно.
- **master.xlsx:** нийтлэг тодорхойлолтод эвдэрсэн 83 хуулбар шатлалыг нийтлэгээр орлуулсан (`ri.py dedup`);
  ганц үйл ажиллагааны 14 шатлал задрахгүй хэвээр (`pytest tests/unit/test_catalog.py -rx`); жингийн нийлбэр
  15=100.3%, 18=101.5%, 28=100.2%, 35=100.02%. master-ийг засаад `python ri.py import master.xlsx --update`.
- **Demo-ийн ТААМАГ хүснэгт:** GRC (аудит, журам, мэдээллийн нууц), ERP_HR_KNOWLEDGE_TEST, JIRA.ACTION_PLAN —
  бодит системийн нэрээр `activities/_shared/sh_010 … 047.sql`, `shared/grc/last_audit.sql`-ийг засна.
