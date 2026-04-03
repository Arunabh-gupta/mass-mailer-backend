-- Email recipients (recruiters, hiring managers, etc.)
-- To migrate from existing recruiters table: ALTER TABLE recruiters RENAME TO contacts;
CREATE TABLE contacts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    company     VARCHAR(255) NOT NULL,
    job_title   VARCHAR(255),
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);