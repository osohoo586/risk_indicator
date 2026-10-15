-- Лавлах: үзүүлэлт (үр дүнгүй ч гэсэн бүгд — UI-д нэр, дугаар, шатлал, бүлэг). Runner run бүрт синк хийнэ.
CREATE TABLE IF NOT EXISTS `{db}`.ri_indicator
(
    indicator_id       String,                         -- RI_01_0002
    indicator_no       String,                         -- 1.2 (харуулах дугаар)
    sort_order         UInt32,
    branch_id          String,
    activity_id        LowCardinality(String),
    group_no           UInt16,
    indicator_name     String,
    score_group        LowCardinality(String),         -- score1 … score6 (master-ийн Score)
    score_group_name   String,
    weight             Nullable(Float64),
    mode               LowCardinality(String),         -- sql / shared / manual
    calc_id            String,
    status             LowCardinality(String),         -- TODO … DONE
    frequency          LowCardinality(String),
    value_unit         LowCardinality(String),
    scale_text         String,
    scale_json         String,                         -- DaHUB score_scale
    source_system      String,
    required_info      String,
    method             String,
    period_text        String,
    owner              String,
    is_active          UInt8,
    synced_at          DateTime64(3) DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(synced_at)
ORDER BY indicator_id;
