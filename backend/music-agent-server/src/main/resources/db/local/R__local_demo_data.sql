INSERT INTO users (
    id, username, password_hash, real_name, role, phone, avatar_url, status, created_at, updated_at
) VALUES
    (1, 'teacher001', '$2a$10$1BhC7mVV4TnE4J3tpyFuz.OAwvfIIkv/bTtObuZiZEAZQHQxcWnvK', '教师001', 'teacher', NULL, NULL, 'active', NOW(), NOW()),
    (2, 'student001', '$2a$10$1BhC7mVV4TnE4J3tpyFuz.OAwvfIIkv/bTtObuZiZEAZQHQxcWnvK', '学生001', 'student', NULL, NULL, 'active', NOW(), NOW())
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO component_definitions (
    component_key, name, category, schema_json, status, created_at, updated_at
) VALUES
    ('scene_display', 'scene display', 'display', '{}', 'active', NOW(), NOW()),
    ('lesson_title_card', 'lesson title card', 'display', '{}', 'active', NOW(), NOW()),
    ('meter_compare', 'meter compare', 'meter', '{}', 'active', NOW(), NOW()),
    ('beat_feedback', 'beat feedback', 'meter', '{}', 'active', NOW(), NOW()),
    ('rhythm_drag_game', 'rhythm drag game', 'rhythm', '{}', 'active', NOW(), NOW()),
    ('creation_panel', 'creation panel', 'creation', '{}', 'active', NOW(), NOW()),
    ('summary_page', 'summary page', 'display', '{}', 'active', NOW(), NOW())
ON DUPLICATE KEY UPDATE component_key = VALUES(component_key);
