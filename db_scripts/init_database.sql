CREATE TABLE logs.message_logs
(
    `platform` LowCardinality(String),
    `platform_user` LowCardinality(String),
    `platform_message_id` LowCardinality(String),
    `is_user_message` Bool,
    `message` String,
    `created_at` DateTime('Europe/Moscow')
)
ENGINE = MergeTree
ORDER BY created_at
SETTINGS index_granularity = 8192;