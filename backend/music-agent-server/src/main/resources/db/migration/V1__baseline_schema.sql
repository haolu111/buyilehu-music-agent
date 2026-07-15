CREATE TABLE users (
    id BIGINT NOT NULL AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL,
    phone VARCHAR(32) NULL,
    avatar_url VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE lesson_plans (
    id BIGINT NOT NULL AUTO_INCREMENT,
    teacher_id BIGINT NOT NULL,
    title VARCHAR(150) NOT NULL,
    source_file_url VARCHAR(255) NULL,
    raw_content TEXT NULL,
    parsed_content TEXT NULL,
    raw_text TEXT NULL,
    parsed_json TEXT NULL,
    parse_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE generation_jobs (
    id BIGINT NOT NULL AUTO_INCREMENT,
    lesson_plan_id BIGINT NOT NULL,
    created_by BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    progress INT NOT NULL DEFAULT 0,
    request_params TEXT NULL,
    error_message TEXT NULL,
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE interactive_packages (
    id BIGINT NOT NULL AUTO_INCREMENT,
    lesson_plan_id BIGINT NULL,
    generation_job_id BIGINT NULL,
    owner_id BIGINT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    current_version_id BIGINT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE package_versions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_no INT NOT NULL,
    created_by BIGINT NOT NULL,
    snapshot_json MEDIUMTEXT NULL,
    remark VARCHAR(255) NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'generated',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE activity_nodes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    parent_node_id BIGINT NULL,
    title VARCHAR(120) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    config_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE component_definitions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    component_key VARCHAR(80) NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    schema_json TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE component_instances (
    id BIGINT NOT NULL AUTO_INCREMENT,
    activity_node_id BIGINT NOT NULL,
    component_definition_id BIGINT NOT NULL,
    instance_name VARCHAR(100) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    props_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE assets (
    id BIGINT NOT NULL AUTO_INCREMENT,
    owner_id BIGINT NULL,
    package_id BIGINT NULL,
    type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NULL,
    file_size BIGINT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE proposal_cards (
    id BIGINT NOT NULL AUTO_INCREMENT,
    generation_job_id BIGINT NULL,
    package_id BIGINT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    confirm_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE quality_reports (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_id BIGINT NULL,
    score INT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    report_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE classes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_name VARCHAR(100) NOT NULL,
    teacher_id BIGINT NOT NULL,
    invite_code VARCHAR(16) NOT NULL,
    description VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_classes_invite_code (invite_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE class_members (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE package_publications (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_id BIGINT NOT NULL,
    class_id BIGINT NOT NULL,
    published_by BIGINT NOT NULL,
    publish_channel VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'published',
    review_enabled TINYINT(1) NOT NULL DEFAULT 0,
    published_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_package_publications_class_id (class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE classroom_sessions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    publication_id BIGINT NOT NULL,
    class_id BIGINT NOT NULL,
    package_id BIGINT NOT NULL,
    teacher_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'not_started',
    course_title VARCHAR(150) NULL,
    course_description TEXT NULL,
    scheduled_start_at DATETIME NULL,
    current_node_id BIGINT NULL,
    started_at DATETIME NULL,
    ended_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_classroom_sessions_publication_id (publication_id),
    KEY idx_classroom_sessions_current_node_id (current_node_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE session_node_states (
    id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    activity_node_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'locked',
    state_json TEXT NULL,
    unlocked_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_progress (
    id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    current_node_id BIGINT NULL,
    progress_status VARCHAR(30) NOT NULL DEFAULT 'not_started',
    progress INT NOT NULL DEFAULT 0,
    score INT NULL,
    wrong_count INT NOT NULL DEFAULT 0,
    hint_used_count INT NOT NULL DEFAULT 0,
    duration_seconds INT NOT NULL DEFAULT 0,
    result_json TEXT NULL,
    last_active_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE learning_events (
    id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    student_id BIGINT NULL,
    activity_node_id BIGINT NULL,
    event_type VARCHAR(80) NOT NULL,
    event_data TEXT NULL,
    occurred_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE package_modify_records (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_id BIGINT NULL,
    modified_by BIGINT NOT NULL,
    modify_type VARCHAR(50) NOT NULL,
    modify_content TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE package_version_diffs (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    from_version_id BIGINT NOT NULL,
    to_version_id BIGINT NOT NULL,
    diff_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
