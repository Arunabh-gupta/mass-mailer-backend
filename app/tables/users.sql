CREATE TABLE IF NOT EXISTS users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_provider    VARCHAR(32) NOT NULL DEFAULT 'clerk',
    provider_user_id VARCHAR(255) NOT NULL UNIQUE,
    email            VARCHAR(255),
    created_at       TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    updated_at       TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);
