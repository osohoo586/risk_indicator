# Шинэ хүний заавар: үзүүлэлт бичих, тестлэх, ажиллуулах

Энэ заавраар явбал эхний өдрөө нэг үзүүлэлтийг source-оос ClickHouse хүртэл бүтэн хийнэ.

## 0. Систем юу хийдэг вэ

```
 master.xlsx (35 үйл ажиллагаа, 1,380 үзүүлэлт) ──ri.py import──► activities/_shared/sh_NNN.sql (50 нийтлэг)
                                                                    activities/act_GG_*/ri_GG_NNNN.sql (448 ганц)
                                                                    │  /*--- master: жин, шатлал, хамрах хугацаа
 python ri.py run <зам> -p 2026-Q3                                   │       тооцоолол: connection, шалгалт ---*/
   1. SQL (эсвэл нийтлэг тооцоолол) source дээр ЗӨВХӨН уншиж        │  SELECT 'SOL' AS ENTITY_LEVEL, SOLID AS ENTITY_ID,
      SOL бүрийн мөр гаргана                                        │         тоологч, хуваарь, VALUE …
   2. үйл ажиллагааны (BRANCHID) SOL-уудаар Σ тоологч / Σ хуваарь   │
   3. шатлалаар оноо (1–5), жин → үйл ажиллагааны нийт оноо         ▼
   4. ClickHouse risk_assessment.ri_result → буцааж уншиж тулгана → audit
```

- **1 тодорхойлолт = 1 `.sql` файл.** Python код бичихгүй. master-ийн 1,380 мөрөөс давхардлыг хасахад 498
  тодорхойлолт: 50 нь олон үйл ажиллагаанд давтагддаг (`activities/_shared/sh_NNN.sql`, үйл ажиллагаа бүрийн
  `activity.yaml shared:`-д №, жин, зөрүү), 448 нь ганц үйл ажиллагааных ([dedup.md](dedup.md)).
- 771 үзүүлэлт автомат (762 нь 34 нийтлэг SQL-ээр, 11 нь өөрийн SQL), 609 нь хүн үнэлнэ (`manual: true` → Excel).
  Чиний ажил гол төлөв: гарын тодорхойлолтыг SQL болгох — нийтлэгийг нэг удаа бичихэд 35 үйл ажиллагаанд тусна.
- SOLID → BRANCHID бүтцийг runner `COREMIS.MAIN`-аас тайлант өдрөөр уншина — SQL-д BRANCHID бичихгүй.
- Нэг үзүүлэлт алдаа өгсөн ч бусад нь үргэлжилнэ.

## 1. Компьютер бэлдэх (нэг удаа)

```bash
git clone <GitLab URL> RA && cd RA
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env                      # DEV_ORACLE_WHOUSE, DEV_CH_* … (нууц үг зөвхөн энд, git-д орохгүй)
git config core.hooksPath .githooks       # commit бүрийн өмнө python3 ri.py check
python ri.py doctor --env dev             # сан, холболт, ClickHouse эрх — бүгд ✔
python ri.py init-db --env dev            # ri_result, audit, history, view
```

**Dev DB-гүйгээр** өөрийн компьютер дээр (Docker дахь Oracle + ClickHouse, стандарт банкны demo DB):

```bash
./tests/local/setup.sh                                              # нэг тушаал (анх удаа ~5 мин)
python ri.py run    --env local activities/act_97_practice/ -p 2026-Q3
python ri.py verify --env local activities/act_97_practice/ -p 2026-Q3
python ri.py show   --env local -i RI_97_9001 -d 2026-09-30         # SOL задаргаа
```

`activities/act_97_practice/` нь дадлагын folder: файл бүрийн доор ClickHouse-д шалгах query бий (DBeaver эсвэл
http://localhost:8123/play). Demo DB-ийн бүтэц: [tests/local/bank_demo.py](../tests/local/bank_demo.py).

## 2. Үзүүлэлт бичих

### 2.1 Файл олох / үүсгэх

Master-ийн мөр бүр аль хэдийн бий (`ri.py import`). Хаана байгааг:

```bash
python ri.py status RI_40_1545          # → activity.yaml-ийн мөр, тодорхойлолт SH_007 (activities/_shared/sh_007.sql)
python ri.py status RI_40_1525          # → activities/act_40_human_resources/ri_40_1525.sql (ганц үйл ажиллагааных)
```

Автоматжуулах гэж шийдсэн бол тэр файлын (нийтлэг бол `sh_NNN.sql`-ийн) `manual: true`-г хасаад доор нь SQL бичнэ.
Master-д байхгүй нэмэлт:

```bash
python ri.py new -a ACT_40 --name-mn "..." --name-en "..."     # → ri_40_9001.sql (жингүй, оноонд орохгүй)
```

### 2.2 Ижил нэртэй үзүүлэлт олон үйл ажиллагаанд байвал

Ижил нэр = НЭГ тодорхойлолт `activities/_shared/sh_NNN.sql` (`python ri.py duplicates` — жагсаалт). SQL нь БҮХ SOL
(эсвэл BRANCHID)-ийн мөр гаргана — үйл ажиллагаа бүр өөрийн SOL-уудаар нэгтгэнэ. Үйл ажиллагаа бүрийн жин, санаатай
өөр шатлал, хугацаа, параметр нь `activity.yaml`-д:

```yaml
shared:
  - {id: RI_40_1545, def: SH_007, weight: 1.5}
  - {id: RI_02_0051, def: SH_029, weight: 1.5, params: {p_pkeys: "..."}}  # (жишээ) энэ үйл ажиллагаанд өөр PKEY
```

Нийтлэг SQL-ийг засах нь 35 үйл ажиллагаанд тусна — `ri.py run activities/_shared/sh_NNN.sql` бүгдийг тооцно.
Нэр нь бага зэрэг өөр ("…-УБ / -ОН") бол тусдаа тодорхойлолт, SQL-ийг `sql_from: SH_NNN` + `params`-аар дахин ашигла.

### 2.3 Тохиргоо (файлын дээд хэсэг)

`# ── Master ──` хэсгийг (жин, шатлал, period_text) гараар засахгүй — master-аас. Чи нэмэх:

```yaml
# ── Тооцоолол ──
description: >
  Томьёо, нэгж (0.95 = 95%), хуучин кодноос юу өөрчилсөн.
connection: oracle_whouse          # clickhouse_dwh (ClickHouse source), clickhouse_ra (өөр үзүүлэлтийн үр дүн)
frequency: quarterly
test_dates: [2026-06-30, 2026-09-30]
source_check: |                    # source бэлэн эсэх (зөвлөмж)
  SELECT COUNT(*) FROM {{schema.coremis}}.GL_REPORT_DATA WHERE TXNDATE = :p_report_date
```

Хамрах хугацааг (`period`) master-ийн "Хамрах хугацаа"-аас runner өөрөө тодорхойлно: тайлант / сүүлийн 1 жил /
аудитаас хойш / сүүлийн үнэлгээ. SQL-д `:p_period_start` … `:p_report_date`.

### 2.4 SQL (`---*/`-ийн доор)

```sql
SELECT 'SOL'                                         AS ENTITY_LEVEL,
       TO_CHAR(e.SOLID)                              AS ENTITY_ID,
       SUM(CASE WHEN … THEN 1 ELSE 0 END)            AS NUMERATOR,      -- тоологч
       COUNT(*)                                      AS DENOMINATOR,    -- хуваарь
       SUM(CASE WHEN … THEN 1 ELSE 0 END) / COUNT(*) AS VALUE
FROM   {{shared.erp.employee_sol}} e
GROUP  BY e.SOLID
```

Дүрэм, бүх параметр, procedure / ClickHouse / ангиллын текстийн жишээ: [sql_standard.md](sql_standard.md).

## 3. Тест хийх

Нэг командаар: ① check → ② dry-run → ③ `test_dates`-ээр ClickHouse-д бичих → ④ үр дүн:

```bash
python ri.py test RI_40_1520 --env dev
python ri.py verify --env dev activities/act_40_human_resources/ri_40_1520.sql -d 2026-09-30   # дахин тооцоолж тулгах
```

Дараа нь **тоог заавал тулгана**: хуучин тайлан / procedure-ийн утгыг `show`-ийн ACTIVITY болон SOL мөртэй
(`python ri.py show --env dev -i RI_40_1520 -d 2026-09-30`), `--save-csv` хийсэн бол `output/dev/*.csv`-тэй.

| Асуудал | Шийдэл |
|---|---|
| Тоо буруу | SQL-ээ засаад дахин run — шинэ мөр бичигдэж, хуучин нь `ri_history`-д |
| Үйл ажиллагааны нийт оноо хуучирсан | `python ri.py aggregate --env dev -a 1006 -d 2026-09-30` |
| Туршилтын датаг устгах | `python ri.py clean --env dev -i RI_40_1520 --audit` (prod-д хориотой) |

## 4. Алдааны мессеж → яах вэ

| Мессеж | Шалтгаан | Засах |
|---|---|---|
| `SKIPPED SOURCE_NOT_READY` | source_check = 0 (тухайн өдрийн дата ачаалагдаагүй) | Ачаалагдсаны дараа `retry --run-id` эсвэл маргаашийн `auto` |
| `SKIPPED PARAMS_TODO` | `params`-д TODO (жнь PKEY) | `config/<env>.yaml params:`-д бөглөнө |
| `FAILED OUTPUT_SCHEMA` | стандарт багана дутуу / илүү | `ENTITY_LEVEL, ENTITY_ID, VALUE` (+ NUMERATOR, DENOMINATOR …) |
| `FAILED BRANCH_NOT_MAPPED` | үйл ажиллагаанд BRANCHID алга | `config/activity_map.csv` |
| `FAILED SOURCE_WRITE_BLOCKED` | SQL / procedure source-д бичих гэсэн | SELECT болгоно (source зөвхөн уншина) |
| `FAILED INSERT_MISMATCH` | ClickHouse-д бичсэн нь буцааж уншихад зөрсөн | бичсэнээ устгасан, хуучин утга хэвээр — дахин run |
| `TIMEOUT` | `timeout_seconds` хэтэрсэн | SQL-ээ хурдасгах эсвэл `timeout_seconds` |
| `VALIDATION_FAILED duplicate` | нэг ENTITY_ID-д олон мөр | `GROUP BY`, JOIN-ийн fan-out |
| `VALIDATION_FAILED min_rows` / `value_range` | мөр дутуу / VALUE хүрээнээс гарсан | source, томьёо |
| `WARNING units_match` | SQL-ийн SOL нэг ч үйл ажиллагааны SOL-той таарсангүй | `ENTITY_ID` = SOLID эсэх (`TO_CHAR(x.SOLID)`) |
| `WARNING scale` | шатлал задарсангүй | `scale: {type: numeric, numericRules: [...]}` гараар |
| `SKIPPED DEPENDENCY_*` | dependency тойрог / алга / амжилтгүй | `dependencies:`-ээ шалгана |
| `ORA-00942`, `ORA-01008` | хүснэгт / параметр | schema alias, `connection`, `:p_xxx` |
| `Env хувьсагч олдсонгүй: DEV_...` | нууц үгийн файл дутуу | `.env`-д нэмнэ |

## 5. Git: хадгалах, review

```bash
git switch main && git pull
git switch -c feature/act_40-ri_40_1525
# ... SQL бичиж, тест хийнэ ...
git add activities/act_40_human_resources/ri_40_1525.sql
git commit -m "feat(ri_40_1525): selection lead time since audit"
python ri.py status RI_40_1525 REVIEW --env dev     # dev дээрх сүүлийн run амжилттай байх ёстой
```

Дараа нь push → GitLab-д Merge Request. CI нь `check` + `pytest`-ийг ажиллуулна. Prod-д `TESTED` / `DONE` л ажиллана.
Дэлгэрэнгүй: [workflow.md](workflow.md).

## 6. Тогтмол ажиллуулах

Prod-д Airflow өдөр бүр `python ri.py auto --env prod --all` ([deploy/airflow_dag.py](../deploy/airflow_dag.py)):
дутуу (шинэ улирал, шинэ файл, өмнө нь source бэлэн биш), алдаатай, SQL нь өөрчлөгдсөн үзүүлэлтийг л ажиллуулна.
Гараар: `python ri.py run --env prod --all -p 2026-Q3`. Гарын үнэлгээ: `ri.py manual template` → бөглөх → `manual load`.

## 7. Runner-ийн код өөрчлөх бол

```bash
pytest                                   # unit тест (DB-гүй) — CI ч ажиллуулна
./tests/local/setup.sh && pytest -m local   # Docker demo DB дээр бүтэн урсгал + эталон (tests/local/demo_check.py)
```

## 8. Хориотой зүйлс

- `.env`, нууц үгийг git-д оруулах, chat эсвэл мессежээр явуулах
- Master-ийн хэсгийг (жин, шатлал) файлд гараар засах — master.xlsx-ээ засаад дахин import
- Бусдын бүлгийн (`act_GG_*`) файлыг owner-той ярилцалгүй засах; `ri_runner/`, `shared/`, `activities/_shared/`-ийг
  тусдаа MR-гүйгээр өөрчлөх (олон үзүүлэлтэд нөлөөлнө)
- Prod ClickHouse дээр гараар `DELETE` / `DROP` — audit-аас ул мөргүй болно
- `status: TESTED`-ийг тоо тулгаагүй үзүүлэлтэд тавих
