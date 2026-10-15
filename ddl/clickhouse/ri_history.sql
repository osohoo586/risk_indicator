-- Дахин ажиллуулахад солигдсон (хуучин) мөрүүдийн түүх. Тоо яагаад өөрчлөгдсөнийг мөрдөнө.
-- Үзүүлэлт бүрийн багана өөр тул мөрийг JSON-оор хадгална. Runner автоматаар үүсгэнэ.
CREATE TABLE IF NOT EXISTS `{db}`.ri_history
(
    indicator_id      LowCardinality(String),
    table_name        String,
    report_date       Date,
    run_id            String,                   -- солигдсон (хуучин) мөрийн run
    replaced_by_run   String,                   -- сольсон (шинэ) run
    archived_at       DateTime64(3) DEFAULT now64(3),
    row_json          String                    -- хуучин мөр бүтнээрээ: {"sol_id":"101","balance_amt":...}
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (indicator_id, report_date, archived_at);
