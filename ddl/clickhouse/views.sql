-- UI-д зориулсан view-ууд (init-db үед CREATE OR REPLACE). ";"-ээр тусгаарласан.
-- Багана бүрт AS нэр заавал (JOIN-д ижил нэртэй багана "a.x" болж гарахаас сэргийлнэ).

-- ① Үйл ажиллагааны нийт оноо (ri_result-ийн TOTAL мөр) + лавлах
CREATE OR REPLACE VIEW `{db}`.v_activity_score AS
SELECT r.snapshot_date AS snapshot_date, r.branch_id AS branch_id, r.activity_id AS activity_id,
       a.group_no AS group_no, r.activity AS activity, r.result_number AS score, r.result AS level,
       r.solid AS solid, a.n_indicators AS n_indicators, a.total_weight AS total_weight, r.loaded_at AS loaded_at
FROM `{db}`.ri_result AS r
LEFT JOIN (SELECT * FROM `{db}`.ri_activity FINAL WHERE is_active = 1) AS a ON a.branch_id = r.branch_id
WHERE r.risk_ind_id = 'TOTAL';

-- ② Үйл ажиллагааны БҮХ үзүүлэлт (үр дүнгүй нь ч — has_result = 0): жин, шатлал, оноо × жин
CREATE OR REPLACE VIEW `{db}`.v_indicator_score AS
SELECT d.snapshot_date AS snapshot_date, i.branch_id AS branch_id, i.activity_id AS activity_id,
       i.indicator_no AS indicator_no, i.sort_order AS sort_order, i.indicator_id AS risk_ind_id,
       i.indicator_name AS risk_indicator, i.score_group AS score_group, i.score_group_name AS score_group_name,
       i.weight AS weight, i.mode AS mode, i.status AS status, i.scale_text AS scale_text,
       i.value_unit AS value_unit, r.result_number AS result_number, r.result AS result,
       toFloat64OrNull(r.result) * i.weight AS contribution, r.solid AS solid, r.loaded_at AS loaded_at,
       r.risk_ind_id != '' AS has_result
FROM (SELECT * FROM `{db}`.ri_indicator FINAL WHERE is_active = 1) AS i
INNER JOIN (SELECT DISTINCT branch_id, snapshot_date FROM `{db}`.ri_result WHERE risk_ind_id = 'TOTAL') AS d
        ON d.branch_id = i.branch_id
LEFT JOIN (SELECT * FROM `{db}`.ri_result WHERE risk_ind_id != 'TOTAL') AS r
        ON r.risk_ind_id = i.indicator_id AND r.snapshot_date = d.snapshot_date
