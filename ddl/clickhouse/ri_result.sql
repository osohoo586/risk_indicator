-- НЭГ үр дүнгийн хүснэгт: мөр = үзүүлэлт × үйл ажиллагаа (BRANCHID) × тайлант өдөр. Runner автоматаар үүсгэнэ.
-- {db} -> config-ийн result.database (risk_assessment)
--   risk_ind_id = RI_GG_NNNN : үзүүлэлтийн үр дүн (result_number = тооцсон утга, result = оноо 1–5)
--   risk_ind_id = TOTAL      : үйл ажиллагааны нийт оноо (result_number = Σ(жин × оноо) / Σ(оноотой жин),
--                              result = эрсдэлийн түвшин Өндөр / Дунд / Бага)
-- solid нь metadata: тайлант өдрийн тухайн BRANCHID-ийн SOLID-ууд ("862,896,897,898"). SOL бүрийн задаргаа хадгалагдахгүй
-- (python ri.py run … --save-csv → output/<env>/*.csv). Техникийн run_id, loaded_at — аль run бичсэн (audit-тай холбоно).
CREATE TABLE IF NOT EXISTS `{db}`.ri_result
(
    activity        String,                          -- үйл ажиллагааны нэр
    activity_id     LowCardinality(String),          -- ACT_40
    solid           String DEFAULT '',               -- үйл ажиллагааны SOLID-ууд (metadata), таслалаар
    branch_id       String,                          -- BRANCHID (1 үйл ажиллагаа = 1 BRANCHID)
    risk_indicator  String,                          -- үзүүлэлтийн нэр
    risk_ind_id     String,                          -- RI_40_1545; TOTAL = нийт оноо
    result_number   Nullable(Float64),               -- тооцсон утга (0.2286 = 22.86%); NULL = өгөгдөл алга
    result          Nullable(String),                -- оноо "1"…"5"; TOTAL: Өндөр / Дунд / Бага; NULL = үнэлэхгүй
    snapshot_date   Date,                            -- тайлант өдөр
    run_id          String,
    loaded_at       DateTime64(3) DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (branch_id, snapshot_date, risk_ind_id);
