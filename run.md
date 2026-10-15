# Ажиллуулах, шалгах

Бүх тушаал project-ийн root-оос (`cd ~/projects/RA`). `python` = `.venv/bin/python`.
Local (Docker) дээр prod-той ижил бүтэцтэй **стандарт банкны demo DB** — нууц үг, dev холболт хэрэггүй.

## 0. Бэлтгэл — нэг тушаал

```bash
./tests/local/setup.sh            # Docker Oracle + ClickHouse, demo DB, init-db (container байвал асаана)
./tests/local/setup.sh --reset    # үр дүнгийн DB (risk_assessment_local)-ийг шинээр
python tests/local/show_dbs.py    # бүх DB, хүснэгт, мөрийн тоо
```

| DB | Юу байна |
|---|---|
| Oracle `localhost:1521/FREEPDB1` (system / oracle_dev) | COREMIS (MAIN, GL_REPORT_DATA, гомдол, төлөвлөгөө …), FINACLE (SOL, CMG, GAM, LAM, ангилал, хүсэлт, RA_LOAN_PKG), ERP (EMPLOYEE_HISTORY, ERP_EMPLOYEE …), CARDZONE, JIRA |
| ClickHouse `localhost:8123` (default / risk_dev) | `cardzone_dwh.card_txn` (source), `risk_assessment_local` (үр дүн) |

Demo DB-ийн бүтэц, өгөгдөл: [tests/local/bank_demo.py](tests/local/bank_demo.py) — нэг seed-ээс (давтан ачаалахад ижил).

## 1. Бүтэн шалгалт — нэг тушаал

```bash
python tests/local/demo_check.py              # seed → run → гарын үнэлгээ → verify → эталон → тохиолдлууд (~1 мин)
python tests/local/demo_check.py --no-seed    # DB-г дахин ачаалахгүй
./tests/local/demo.sh --step                  # алхам бүрийг тайлбартай, Enter дарж
```

Хүлээгдэх төгсгөл: `АМЖИЛТТАЙ: эталон 2764/2764, нийт оноо 70/70, тохиолдол 20/20, verify rc=0`.
Тайлан: `output/demo_report.html`. Юуг шалгадаг: [docs/examples.md](docs/examples.md).

## 2. Ажиллуулах

```bash
python ri.py run --env local activities/act_40_human_resources/ -p 2026-Q3          # нэг үйл ажиллагаа
python ri.py run --env local activities/act_40_human_resources/ri_40_1520.sql -d 2026-09-30
python ri.py run --env local activities/_shared/sh_007.sql -p 2026-Q3               # 35 үйл ажиллагааны эргэц
python ri.py run --env local --all -p 2026-Q2 -p 2026-Q3                             # бүгд (305 автомат)
python ri.py run --env local -a 1006 -p 2026-Q3 --dry-run                            # SQL, багана — бичихгүй
```

Хугацаа: `-p 2026-Q3` (эхлэл 07-01, төгсгөл 09-30; олон удаа өгч болно), `-d 2026-09-30` (эхлэл нь frequency-оос),
`--from 2026-01-01 --to 2026-09-30` (давтамжийн огноонуудаар backfill), эсвэл юу ч өгөхгүй бол `config/period.yaml`.
Үзүүлэлт бүрийн жинхэнэ эхлэл нь `period`-оос: сүүлийн 1 жил, аудитаас хойш г.м. (`:p_period_start`).

```
INFO    RI_40_1520 2026-09-30 SUCCESS              0.3s value=0.226 score=5
INFO    RI_40_1545 2026-09-30 SUCCESS              0.1s value=0.2286 score=5
INFO    RI_40_1542 2026-09-30 SUCCESS              0.1s value=1 score=1
…
ACT_40         12            12

ҮЙЛ АЖИЛЛАГААНЫ ОНОО  (Σжин×оноо / Σоноотой жин):
  1006 ACT_40 2026-09-30   3.16 Дунд   оноотой 38/47  жингийн хамралт 78%
```

`оноотой 38/47`: 47 үзүүлэлтээс 38 нь оноотой (үлдсэн нь гарын үнэлгээ бөглөөгүй / Үнэлэхгүй).

**Гарын үнэлгээ** (609 үзүүлэлт):

```bash
python ri.py manual template -a 1006 -d 2026-09-30           # output/manual/manual_1006_20260930.xlsx
#   VALUE (тоо / хувь), VALUE_TEXT (шатлалын ангилал) эсвэл SCORE (0–5)-ийг бөглөнө
python ri.py manual load output/manual/manual_1006_20260930.xlsx --env local [--dry-run]
```

## 3. ClickHouse-д юу бичигдэх вэ

`risk_assessment_local.ri_result` — нэг хүснэгт:

| row_type | entity_level | Мөр |
|---|---|---|
| INDICATOR | ACTIVITY | үзүүлэлт × үйл ажиллагаа: value, numerator, denominator, value_text, **score**, weight, branch_id, **sol_id** (үйл ажиллагааны SOLID-ууд), file_name, period_start |
| INDICATOR | SOL / BANK / … | задаргаа (SOL бүрийн тоологч, хуваарь, утга) |
| ACTIVITY | ACTIVITY | үйл ажиллагааны нийт оноо (value), level (Өндөр ≥ 3.5, Дунд ≥ 2.5, Бага), n_scored, weight_coverage |

```sql
-- Үзүүлэлт бүр (хуучин risk_indicators-ийн хэлбэр)
SELECT indicator_id, ra_name, branch_id, sol_id, scale, scale_text, score, last_workdate
FROM   risk_assessment_local.v_risk_indicators
WHERE  branch_id = '1006' AND last_workdate = '2026-09-30' ORDER BY indicator_id;

-- Бүх үйл ажиллагааны нийт оноо
SELECT report_date, branch_id, activity_name, round(score, 2) AS score, level, n_scored, n_indicators
FROM   risk_assessment_local.v_activity_score ORDER BY report_date, score DESC;
```

`python tests/local/ch_query.py "SQL"` эсвэл DBeaver / http://localhost:8123/play. UI-д: [docs/ui_tables.md](docs/ui_tables.md).
Мөн: `python ri.py show --env local -i RI_40_1545 -d 2026-09-30` (SOL задаргаа), `-a 1006` (үйл ажиллагаа),
`python ri.py report --env local -a 1006 -d 2026-09-30 --open` (HTML).

### Бичилтийн баталгаа

- Source-ийг зөвхөн уншина (Oracle READ ONLY transaction, ClickHouse readonly=2).
- Бичсэн мөр бүрийг ClickHouse-оос буцааж уншиж тулгана; зөрвөл устгаж `FAILED [INSERT_MISMATCH]`.
- Дахин ажиллуулахад хуучин мөр `ri_history`-д шилжиж устгагдана; DELETE-ийн дараа үлдсэн эсэхийг заавал шалгана
  (үлдвэл дахин, бүтэхгүй бол `FAILED [DELETE_INCOMPLETE]` — давхардсан мөр чимээгүй үлдэхгүй).
- Run бүр `ri_execution_audit`-д (төлөв, шалтгаан, хугацаа, sql_version).

## 4. Шалгах

```bash
python ri.py check --env local                                         # static (DB-гүй)
python ri.py verify --env local activities/act_40_human_resources/ -p 2026-Q3
```

```
  ✔ RI_40_1520 2026-09-30  value=0.226044 score=5  (1 мөр, 1006)
  ✔ RI_40_1545 2026-09-30  value=0.228571 score=5  (5 мөр, 1006)
  ✔ 1006 ACT_40 2026-09-30 нийт оноо 3.160 Дунд (оноотой 38)
VERIFY: таарсан 13, зөрүүтэй 0, алгассан 0
```

`verify` нь source дээр дахин тооцоолж ClickHouse-ийн мөр бүртэй (ACTIVITY + задаргаа, sol_id, file_name, оноо),
audit-тай, үйл ажиллагааны нийт оноог үзүүлэлтүүдээс нь тулгана. Зөрвөл exit 1.

```bash
python ri.py auto --env local --all --plan --as-of 2026-10-14 --since 2026-07-01
# AUTO 2026-07-01 … 2026-10-14: бүх үр дүн шинэчлэгдсэн, ажиллуулах зүйл алга.
```

## 5. Дадлага: шинэ үзүүлэлт бичих

`activities/act_97_practice/` (BRANCHID 1500 — салбарын сүлжээ, `example: true`). Файл бүрийн доор ClickHouse-д
шалгах query бий: run-ээс өмнө (а) → БАЙХГҮЙ, дараа нь → БАЙНА, (б) үйл ажиллагааны утга, (в) SOL задаргаа.

```bash
python ri.py run    --env local activities/act_97_practice/ri_97_9001.sql -p 2026-Q3
python ri.py verify --env local activities/act_97_practice/ -p 2026-Q3
```

## 6. Unit тест

```bash
pytest                     # DB-гүй: runner + үзүүлэлт бүр (1,388) + тодорхойлолт бүр (50)
pytest -m local            # Docker дээр demo_check бүтнээр (Docker асаагүй бол skip)
```

## 7. Асуудал гарвал

| Шинж | Шалтгаан / шийдэл |
|---|---|
| `Connection refused` 1521 / 8123 | Docker Desktop асаагаад `./tests/local/setup.sh` |
| Нэг run ~7 минут гацсан мэт | Docker-ийн VM унтсан (`docker logs risk-oracle | grep 'Time drifted'`) — runner гацаагүй |
| `ORA-00942` | demo DB ачаалагдаагүй: `python tests/local/seed_bank.py` |
| `SKIPPED PARAMS_TODO` (SH_029 …) | `config/<env>.yaml params:`-д PKEY (local-д бий) |
| `FAILED BRANCH_NOT_MAPPED` | үйл ажиллагаанд BRANCHID алга (`config/activity_map.csv`; local: `tests/local/demo/activity_map.csv`) |
| Холболт, эрх | `python ri.py doctor --env local` |
