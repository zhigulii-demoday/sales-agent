CREATE TABLE logs.message_logs
(
    `platform` LowCardinality(String),
    `platform_id` LowCardinality(String),
    `our_message` Bool,
    `message` String,
    `created_at` DateTime('Europe/Moscow')
)
ENGINE = MergeTree
ORDER BY created_at
SETTINGS index_granularity = 8192;