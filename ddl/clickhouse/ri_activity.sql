-- Лавлах: үйл ажиллагаа (1 BRANCHID = 1 үйл ажиллагаа). Runner run бүрт activities/-аас синк хийнэ.
CREATE TABLE IF NOT EXISTS `{db}`.ri_activity
(
    branch_id          String,
    activity_id        LowCardinality(String),         -- ACT_01 (master-ийн бүлэг)
    group_no           UInt16,
    activity_name      String,
    activity_name_old  String,
    n_indicators       UInt32,
    total_weight       Float64,
    is_active          UInt8,
    synced_at          DateTime64(3) DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(synced_at)
ORDER BY branch_id;
