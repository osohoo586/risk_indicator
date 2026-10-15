# Үр дүнгийн хүснэгт, UI / dashboard-д зориулсан view

Бүх үр дүн **НЭГ хүснэгтэд**: `risk_assessment.ri_result` (local: `risk_assessment_local`). Runner,
`ri.py manual load` автоматаар бичнэ; `ri.py init-db` (эсвэл анхны run) үүсгэнэ — DDL: `ddl/clickhouse/ri_result.sql`.

## ri_result

Мөр = үзүүлэлт × үйл ажиллагаа (BRANCHID) × тайлант өдөр. Үйл ажиллагааны нийт оноо нь `risk_ind_id = 'TOTAL'` мөр.

| Багана | Төрөл | Утга |
|---|---|---|
| `activity` | String | үйл ажиллагааны нэр |
| `activity_id` | String | ACT_40 (master-ийн бүлэг) |
| `solid` | String | **metadata**: тайлант өдрийн тухайн BRANCHID-ийн SOLID-ууд, таслалаар ("862,896,897,898"). Бүтэц өөрчлөгдвөл өдөр бүрт өөр |
| `branch_id` | String | BRANCHID (1 үйл ажиллагаа = 1 BRANCHID, нэг BRANCHID-д олон SOLID) |
| `risk_indicator` | String | үзүүлэлтийн нэр; TOTAL мөрөнд "Нийт оноо" |
| `risk_ind_id` | String | RI_40_1545; TOTAL |
| `result_number` | Nullable(Float64) | тооцсон утга (харьцаа 0–1: 0.2286 = 22.86%); TOTAL: Σ(жин × оноо) / Σ(оноотой жин). NULL = өгөгдөл алга |
| `result` | Nullable(String) | оноо "1"…"5"; TOTAL: эрсдэлийн түвшин (Өндөр ≥ 3.5, Дунд ≥ 2.5, Бага). NULL = үнэлэхгүй |
| `snapshot_date` | Date | тайлант өдөр |
| `run_id`, `loaded_at` | техникийн | аль run, хэзээ бичсэн (`ri_execution_audit`-тай холбоно) |

`ORDER BY (branch_id, snapshot_date, risk_ind_id)`, сараар partition. Дахин ажиллуулахад тухайн түлхүүрийн мөр
солигдоно (хуучин нь `ri_history`-д) — давхардахгүй.

```sql
-- Нэг үйл ажиллагааны бүх үр дүн
SELECT risk_ind_id, risk_indicator, result_number, result, solid
FROM risk_assessment.ri_result
WHERE branch_id = '1006' AND snapshot_date = '2026-09-30'
ORDER BY risk_ind_id = 'TOTAL' DESC, risk_ind_id;

-- Бүх үйл ажиллагааны нийт оноо
SELECT branch_id, activity, result_number AS score, result AS level, solid
FROM risk_assessment.ri_result
WHERE risk_ind_id = 'TOTAL' AND snapshot_date = '2026-09-30'
ORDER BY score DESC;

-- SOLID-оор хайх (metadata): 862-г агуулсан үйл ажиллагаа
SELECT DISTINCT branch_id, activity FROM risk_assessment.ri_result
WHERE has(splitByChar(',', solid), '862') AND snapshot_date = '2026-09-30';
```

Хадгалахгүй зүйл: SOL бүрийн задаргаа, тоологч / хуваарь, жин, шатлал. Задаргааг `python ri.py run … --save-csv`
(`output/<env>/*.csv`), жин / шатлалыг доорх лавлах хүснэгт, `activities/`-аас.

## Техникийн хүснэгт (runner өөрөө бөглөнө)

| Хүснэгт | Юу |
|---|---|
| `ri_execution_audit` | үзүүлэлт бүрийн ажилласан бүртгэл: төлөв, алдааны код, хугацаа, мөрийн тоо, sql_version, гарын үнэлгээний COMMENT |
| `ri_history` | дахин ажиллуулахад солигдсон хуучин мөрүүд (JSON) |
| `ri_activity`, `ri_indicator` | `activities/`-ийн лавлах: нэр, жин, шатлал, Score бүлэг (ReplacingMergeTree, `FINAL`) |

## View (UI)

```sql
-- ① Бүх үйл ажиллагааны нийт оноо
SELECT branch_id, activity, score, level, solid, n_indicators
FROM risk_assessment.v_activity_score
WHERE snapshot_date = '2026-09-30' ORDER BY score DESC;

-- ② Нэг үйл ажиллагааны БҮХ үзүүлэлт (үр дүнгүй нь ч), Score бүлгээр
SELECT indicator_no, risk_ind_id, risk_indicator, score_group, weight, mode, has_result,
       result_number, result, contribution, scale_text
FROM risk_assessment.v_indicator_score
WHERE branch_id = '1006' AND snapshot_date = '2026-09-30'
ORDER BY sort_order;
```

- `has_result = 0` → үр дүн алга (SQL бичигдээгүй / manual бөглөөгүй) — UI-д "Мэдээлэл алга".
- `contribution` = оноо × жин; нийт оноо = Σcontribution / Σ(оноотой жин).
- `result_number` харьцаа (0.95) бол `value_unit = 'ratio'`, шатлал %-аар бол UI ×100 хийж харуулна.

## Улирлын хандлага

```sql
SELECT snapshot_date, result_number AS score, result AS level FROM risk_assessment.ri_result
WHERE branch_id = '1006' AND risk_ind_id = 'TOTAL' ORDER BY snapshot_date;
```

## UI-гүйгээр харах

```bash
python ri.py show   --env dev -a 1006 -d 2026-09-30            # үйл ажиллагааны бүх мөр
python ri.py report --env dev -a 1006 -d 2026-09-30 --open     # output/report_1006_20260930.html
```

Score бүлгийн нэрийг `config/scoring.yaml`-д засна. Хуучин бүтэцтэй `ri_result` байвал `init-db` түүнийг
`ri_result_legacy_YYYYMMDDHHMMSS` нэрээр хадгалаад (устгахгүй) шинийг үүсгэнэ.
