-- Үзүүлэлт бүрийн ажиллагааны бүртгэл (амжилттай / амжилтгүй / алгассан).
-- Runner автоматаар үүсгэнэ (python ri.py init-db). {db} -> config-ийн result.database
CREATE TABLE IF NOT EXISTS `{db}`.ri_execution_audit
(
    run_id             String,
    run_mode           LowCardinality(String),            -- RUN / DRY_RUN / RETRY
    activity_id        LowCardinality(String),
    indicator_id       LowCardinality(String),
    report_date        Date,
    period_start       Nullable(Date),                    -- SQL-д өгсөн :p_period_start
    execution_status   LowCardinality(String),            -- SUCCESS / WARNING / FAILED / TIMEOUT / VALIDATION_FAILED / SKIPPED / DRY_RUN_OK
    started_at         DateTime64(3),
    finished_at        Nullable(DateTime64(3)),
    duration_seconds   Nullable(Float64),
    affected_rows      Nullable(Int64),                   -- Устгагдсан хуучин мөрийн тоо
    source_row_count   Nullable(Int64),
    result_row_count   Nullable(Int64),
    validation_detail  Nullable(String),
    error_code         Nullable(String),
    error_message      Nullable(String),
    executed_by        String,
    environment        LowCardinality(String),
    sql_version        Nullable(String),
    connection_name    Nullable(String),
    target_table       Nullable(String),                  -- Үр дүн бичигдсэн хүснэгт (ri_01_002)
    created_at         DateTime64(3) DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (indicator_id, report_date, started_at);
