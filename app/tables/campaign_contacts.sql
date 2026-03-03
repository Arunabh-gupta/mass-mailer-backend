CREATE TABLE campaign_contacts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id   UUID NOT NULL,
    contact_id    UUID NOT NULL,
    status        VARCHAR(32) NOT NULL,
    sent_at       TIMESTAMP,
    error_message TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    CONSTRAINT uq_campaign_contact UNIQUE (campaign_id, contact_id)
);

