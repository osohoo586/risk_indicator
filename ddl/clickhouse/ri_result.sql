-- НЭГ эцсийн үр дүнгийн хүснэгт. Гол түлхүүр: branch_id (1 BRANCHID = 1 үйл ажиллагаа). Runner автоматаар үүсгэнэ. {db} -> config-ийн result.database
--   row_type = INDICATOR : үзүүлэлтийн утга, оноо, жин (entity_level ACTIVITY = үйл ажиллагааны утга,
--                          SOL = drill-down мөр)
--   row_type = ACTIVITY  : үйл ажиллагааны нийт оноо = Σ(жин × оноо) / Σ(оноотой үзүүлэлтийн жин), түвшин
CREATE TABLE IF NOT EXISTS `{db}`.ri_result
(
    report_date      Date,
    period_start     Nullable(Date),
    row_type         LowCardinality(String),
    group_no         UInt16,
    activity_id      LowCardinality(String),          -- master-ийн бүлэг (ACT_01) — лавлах
    branch_id        String,                          -- ★ үйл ажиллагааны түлхүүр (BRANCHID)
    sol_id           String DEFAULT '',               -- SOL мөрөнд тухайн SOLID; ACTIVITY мөрөнд үйл ажиллагааны SOLID-ууд "808,810"
    activity_name    String,
    indicator_id     String,
    indicator_name   String,
    calc_id          String,
    source_kind      LowCardinality(String),          -- SQL / SHARED / MANUAL
    file_name        String DEFAULT '',               -- activities/act_GG_slug/ri_GG_NNNN.sql
    entity_level     LowCardinality(String),          -- ACTIVITY / SOL / BANK / ...
    entity_id        String,
    entity_name      Nullable(String),
    parent_id        Nullable(String),
    metric           LowCardinality(String),
    numerator        Nullable(Float64),
    denominator      Nullable(Float64),
    value            Nullable(Float64),
    value_text       Nullable(String),                -- гараар оруулсан текст утга ("Тийм" гэх мэт)
    score            Nullable(Float64),               -- 1–5; NULL = үнэлэхгүй / шатлалгүй
    score_label      Nullable(String),
    weight           Nullable(Float64),
    level            LowCardinality(String) DEFAULT '',  -- Өндөр / Дунд / Бага
    n_indicators     Nullable(UInt32),
    n_scored         Nullable(UInt32),
    weight_coverage  Nullable(Float64),
    data_status      LowCardinality(String) DEFAULT 'OK',
    score_type       LowCardinality(String) DEFAULT '',
    scale_version    String DEFAULT '',
    source_row_count Nullable(Int64),
    comment          Nullable(String),
    entered_by       Nullable(String),
    run_id           String,
    sql_version      String DEFAULT '',
    loaded_at        DateTime64(3) DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (branch_id, report_date, row_type, indicator_id, entity_level, entity_id, metric);
