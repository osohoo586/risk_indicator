-- UI-д зориулсан view-ууд (init-db үед CREATE OR REPLACE). ";"-ээр тусгаарласан.
-- Багана бүрт AS нэр заавал (JOIN-д ижил нэртэй багана "a.x" болж гарахаас сэргийлнэ).

-- ① Бүх үйл ажиллагааны нийт оноо
CREATE OR REPLACE VIEW `{db}`.v_activity_score AS
SELECT r.report_date AS report_date, r.branch_id AS branch_id, a.activity_id AS activity_id,
       a.group_no AS group_no, a.activity_name AS activity_name,
       r.value AS score, r.level AS level, r.n_scored AS n_scored, r.n_indicators AS n_indicators,
       r.weight_coverage AS weight_coverage, r.weight AS total_weight, r.loaded_at AS loaded_at
FROM `{db}`.ri_result AS r
INNER JOIN (SELECT * FROM `{db}`.ri_activity FINAL WHERE is_active = 1) AS a ON a.branch_id = r.branch_id
WHERE r.row_type = 'ACTIVITY';

-- ② Үйл ажиллагааны БҮХ үзүүлэлт (үр дүнгүй нь ч — has_result = 0), дугаар, бүлгээр
CREATE OR REPLACE VIEW `{db}`.v_indicator_score AS
SELECT d.report_date AS report_date, i.branch_id AS branch_id, i.activity_id AS activity_id,
       i.indicator_no AS indicator_no, i.sort_order AS sort_order, i.indicator_id AS indicator_id,
       i.indicator_name AS indicator_name, i.score_group AS score_group, i.score_group_name AS score_group_name,
       i.weight AS weight, i.mode AS mode, i.status AS status, i.scale_text AS scale_text,
       i.value_unit AS value_unit, r.source_kind AS source_kind, r.value AS value, r.value_text AS value_text,
       r.numerator AS numerator, r.denominator AS denominator, r.score AS score, r.score_label AS score_label,
       r.score * i.weight AS contribution, r.comment AS comment, r.entered_by AS entered_by,
       r.loaded_at AS loaded_at, r.indicator_id != '' AS has_result
FROM (SELECT * FROM `{db}`.ri_indicator FINAL WHERE is_active = 1) AS i
INNER JOIN (SELECT DISTINCT branch_id, report_date FROM `{db}`.ri_result WHERE row_type = 'ACTIVITY') AS d
        ON d.branch_id = i.branch_id
LEFT JOIN (SELECT * FROM `{db}`.ri_result WHERE row_type = 'INDICATOR' AND entity_level = 'ACTIVITY') AS r
        ON r.indicator_id = i.indicator_id AND r.report_date = d.report_date;

-- ③ Үзүүлэлтийн SOL (болон бусад түвшний) задаргаа
CREATE OR REPLACE VIEW `{db}`.v_indicator_detail AS
SELECT r.report_date AS report_date, r.branch_id AS branch_id, i.indicator_no AS indicator_no,
       r.indicator_id AS indicator_id, i.indicator_name AS indicator_name, r.entity_level AS entity_level,
       r.entity_id AS entity_id, r.entity_name AS entity_name, r.metric AS metric,
       r.numerator AS numerator, r.denominator AS denominator, r.value AS value
FROM `{db}`.ri_result AS r
LEFT JOIN (SELECT indicator_id, indicator_no, indicator_name FROM `{db}`.ri_indicator FINAL) AS i
       ON i.indicator_id = r.indicator_id
WHERE r.row_type = 'INDICATOR' AND r.entity_level != 'ACTIVITY'
;

-- ④ Нэг мөр = үзүүлэлт × үйл ажиллагаа × тайлант өдөр (хуучин risk_indicators-ийн хэлбэр — DBeaver, BI-д)
--    scale = үйл ажиллагааны утга, scale_text = ангиллын текст, sol_id = үйл ажиллагааны SOLID-ууд, last_workdate =
--    тайлант өдөр. ri_result-д scope бүрт хамгийн сүүлийн run л үлддэг (хуучин нь ri_history-д) тул давхардахгүй.
CREATE OR REPLACE VIEW `{db}`.v_risk_indicators AS
SELECT r.indicator_id AS indicator_id, r.activity_id AS activity_id, r.activity_name AS activity_name,
       r.file_name AS file_name, r.indicator_name AS ra_name, r.branch_id AS branch_id, r.sol_id AS sol_id,
       r.metric AS metric, r.value AS scale, r.value_text AS scale_text, r.numerator AS numerator,
       r.denominator AS denominator, r.score AS score, r.score_label AS score_label, r.weight AS weight,
       r.source_kind AS source_kind, r.period_start AS period_start, r.report_date AS last_workdate,
       r.run_id AS run_id, r.loaded_at AS loaded_at
FROM `{db}`.ri_result AS r
WHERE r.row_type = 'INDICATOR' AND r.entity_level = 'ACTIVITY'
