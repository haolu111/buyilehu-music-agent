CREATE TABLE classes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_name VARCHAR(100) NOT NULL,
    teacher_id BIGINT NOT NULL,
    description VARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE class_members (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE lesson_plans (
    id BIGINT NOT NULL AUTO_INCREMENT,
    teacher_id BIGINT NOT NULL,
    title VARCHAR(150) NOT NULL,
    source_file_url VARCHAR(255) NULL,
    raw_content TEXT NULL,
    parsed_content TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

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
);

CREATE TABLE interactive_packages (
    id BIGINT NOT NULL AUTO_INCREMENT,
    lesson_plan_id BIGINT NULL,
    generation_job_id BIGINT NULL,
    owner_id BIGINT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE package_versions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_no INT NOT NULL,
    created_by BIGINT NOT NULL,
    snapshot_json TEXT NULL,
    remark VARCHAR(255) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE proposal_cards (
    id BIGINT NOT NULL AUTO_INCREMENT,
    generation_job_id BIGINT NULL,
    package_id BIGINT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

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
);

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
);

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
);

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
);

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
);

CREATE TABLE package_publications (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    version_id BIGINT NOT NULL,
    published_by BIGINT NOT NULL,
    publish_channel VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'published',
    published_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE classroom_sessions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    class_id BIGINT NOT NULL,
    package_id BIGINT NOT NULL,
    teacher_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'not_started',
    started_at DATETIME NULL,
    ended_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE session_node_states (
    id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    activity_node_id BIGINT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'locked',
    state_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE student_progress (
    id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    current_node_id BIGINT NULL,
    progress INT NOT NULL DEFAULT 0,
    score INT NULL,
    last_active_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);

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
);

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
);

CREATE TABLE package_version_diffs (
    id BIGINT NOT NULL AUTO_INCREMENT,
    package_id BIGINT NOT NULL,
    from_version_id BIGINT NOT NULL,
    to_version_id BIGINT NOT NULL,
    diff_json TEXT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
);
