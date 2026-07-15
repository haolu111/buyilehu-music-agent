ALTER TABLE interactive_packages
    ADD COLUMN lock_version BIGINT NOT NULL DEFAULT 0;

ALTER TABLE activity_nodes
    ADD COLUMN lock_version BIGINT NOT NULL DEFAULT 0;

ALTER TABLE generation_jobs
    ADD COLUMN idempotency_key VARCHAR(64) NULL,
    ADD COLUMN request_hash VARCHAR(64) NULL;

CREATE UNIQUE INDEX uk_generation_jobs_creator_idempotency
    ON generation_jobs (created_by, idempotency_key);
