ALTER TABLE package_publications ADD COLUMN class_id BIGINT NULL;
ALTER TABLE package_publications ADD COLUMN review_enabled BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE package_publications ADD INDEX idx_package_publications_class_id (class_id);

ALTER TABLE classroom_sessions ADD COLUMN publication_id BIGINT NULL;
ALTER TABLE classroom_sessions ADD COLUMN current_node_id BIGINT NULL;
ALTER TABLE classroom_sessions ADD INDEX idx_classroom_sessions_publication_id (publication_id);
ALTER TABLE classroom_sessions ADD INDEX idx_classroom_sessions_current_node_id (current_node_id);

ALTER TABLE session_node_states ADD COLUMN unlocked_at DATETIME NULL;
