ALTER TABLE interactive_packages ADD COLUMN current_version_id BIGINT;

ALTER TABLE package_versions ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'generated';

ALTER TABLE proposal_cards ADD COLUMN confirm_status VARCHAR(30) NOT NULL DEFAULT 'pending';
