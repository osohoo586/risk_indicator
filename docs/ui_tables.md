# UI / dashboard-д зориулсан хүснэгт, view

UI нь **3 view**-ээс уншина (+ `v_risk_indicators` — үзүүлэлт бүр нэг мөр, BI / DBeaver-т). Хүснэгтүүдийг runner,
`ri.py manual load` автоматаар бөглөнө. Database: prod/dev `risk_assessment`, local `risk_assessment_local`.

```
 ri_activity  (лавлах: үйл ажиллагаа)  ─┐
 ri_indicator (лавлах: үзүүлэлт, үр      ├──▶  v_activity_score    ① бүх үйл ажиллагааны оноо
               дүнгүй нь ч, 1.1 дугаар,  │     v_indicator_score   ② нэг branch_id-ийн БҮХ үзүүлэлт
               шатлал, бүлэг)            │     v_indicator_detail  ③ үзүүлэлтийн SOL задаргаа
 ri_result    (үр дүн: утга, оноо, SOL) ─┘
```

| Хүснэгт / view | Түлхүүр | Хэзээ шинэчлэгдэх |
|---|---|---|
| `ri_activity` | `branch_id` | run, manual load, init-db бүрт `activities/`-аас синк (ReplacingMergeTree, `FINAL`) |
| `ri_indicator` | `indicator_id` | мөн адил. Устгагдсан үзүүлэлт `is_active = 0` |
| `ri_result` | `branch_id, report_date, …` | run, manual load |

## ① Нүүр: бүх үйл ажиллагаа

```sql
SELECT branch_id, activity_name, score, level, n_scored, n_indicators, weight_coverage
FROM risk_assessment.v_activity_score
WHERE report_date = '2026-09-30'
ORDER BY score DESC;
```

## ② Нэг үйл ажиллагаа: үзүүлэлтүүд (1.1, 1.2 …), Score бүлгээр

```sql
SELECT indicator_no, indicator_name, score_group, score_group_name, weight, mode,
       has_result, value, value_text, score, score_label, contribution, comment, scale_text
FROM risk_assessment.v_indicator_score
WHERE branch_id = '998' AND report_date = '2026-09-30'
ORDER BY sort_order;
```

- `has_result = 0` → үр дүн алга (SQL бичигдээгүй / manual бөглөөгүй) — UI-д "Мэдээлэл алга" гэж харуулна.
- `contribution` = оноо × жин; нийт оноо = Σcontribution / Σ(оноотой жин).
- Бүлгийн дүн: `GROUP BY score_group`.
- `value` харьцаа (0.95) бол `value_unit = 'ratio'`, шатлал %-аар бол UI ×100 хийж харуулна.

## ③ Үзүүлэлт дээр дарахад: SOL задаргаа

```sql
SELECT entity_id AS sol, entity_name, numerator, denominator, value
FROM risk_assessment.v_indicator_detail
WHERE branch_id = '998' AND indicator_id = 'RI_01_0002' AND report_date = '2026-09-30'
ORDER BY value;
```

## Үзүүлэлт бүр нэг мөр (хуучин risk_indicators-ийн хэлбэр)

```sql
SELECT indicator_id, ra_name, activity_name, branch_id, sol_id, scale, scale_text, score, weight, last_workdate
FROM risk_assessment.v_risk_indicators
WHERE last_workdate = '2026-09-30' AND branch_id = '998'
ORDER BY indicator_id;
```

`sol_id` = тухайн өдрийн бүтцээр үйл ажиллагааны SOLID-ууд ("808,810,…"), `scale` = үйл ажиллагааны утга.

## Улирлын хандлага

```sql
SELECT report_date, score, level FROM risk_assessment.v_activity_score
WHERE branch_id = '998' ORDER BY report_date;
```

## UI-гүйгээр харах

```bash
python ri.py report --env dev -a 998 -d 2026-09-30 --open   # output/report_998_20260930.html
```

Score бүлгийн нэрийг `config/scoring.yaml`-д засна.
