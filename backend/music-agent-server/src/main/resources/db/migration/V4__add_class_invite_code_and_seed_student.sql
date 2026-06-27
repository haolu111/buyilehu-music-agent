ALTER TABLE classes ADD COLUMN invite_code VARCHAR(16) NULL;
ALTER TABLE classes ADD CONSTRAINT uk_classes_invite_code UNIQUE (invite_code);

INSERT INTO users (username, password_hash, real_name, role, phone, avatar_url, status, created_at, updated_at)
VALUES ('student001', '$2a$10$1BhC7mVV4TnE4J3tpyFuz.OAwvfIIkv/bTtObuZiZEAZQHQxcWnvK', '学生001', 'student', NULL, NULL, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
