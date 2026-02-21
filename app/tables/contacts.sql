-- Email recipients (recruiters, hiring managers, etc.)
-- To migrate from existing recruiters table: ALTER TABLE recruiters RENAME TO contacts;
CREATE TABLE contacts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    company     VARCHAR(255) NOT NULL,
    role        VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);