-- =========================================================
-- “不亦乐乎”音乐课堂智能体系统数据库建表脚本
-- 适用数据库：MySQL 8.0+
-- 字符集：utf8mb4
-- 说明：
-- 1. 本脚本包含教师端、学生端、教案、互动包、活动链、课堂控制、学习数据、二次修改等核心表。
-- 2. JSON 字段用于存储活动链、组件配置、解析结果、质量检查明细等半结构化数据。
-- 3. 已发布课堂数据通过 package_version_id 与具体作品包版本绑定，避免后续修改导致数据错乱。
-- =========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS buyilehu_music_agent
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE buyilehu_music_agent;

-- =========================================================
-- 0. 清理旧表：按外键依赖倒序删除
-- =========================================================

DROP TABLE IF EXISTS package_version_diffs;
DROP TABLE IF EXISTS package_modify_records;
DROP TABLE IF EXISTS learning_events;
DROP TABLE IF EXISTS student_progress;
DROP TABLE IF EXISTS session_node_states;
DROP TABLE IF EXISTS classroom_sessions;
DROP TABLE IF EXISTS package_publications;
DROP TABLE IF EXISTS quality_reports;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS component_instances;
DROP TABLE IF EXISTS activity_nodes;
DROP TABLE IF EXISTS proposal_cards;
DROP TABLE IF EXISTS generation_jobs;
DROP TABLE IF EXISTS package_versions;
DROP TABLE IF EXISTS interactive_packages;
DROP TABLE IF EXISTS component_definitions;
DROP TABLE IF EXISTS lesson_plans;
DROP TABLE IF EXISTS class_members;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================
-- 1. users 用户表
-- =========================================================

CREATE TABLE users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(64) NOT NULL COMMENT '登录账号',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  real_name VARCHAR(64) NOT NULL COMMENT '真实姓名',
  role VARCHAR(20) NOT NULL COMMENT '用户角色：teacher / student',
  phone VARCHAR(32) NULL COMMENT '手机号',
  avatar_url VARCHAR(500) NULL COMMENT '头像地址',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '账号状态：active / disabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_username (username),
  KEY idx_users_role (role),
  KEY idx_users_status (status),
  CONSTRAINT chk_users_role CHECK (role IN ('teacher', 'student')),
  CONSTRAINT chk_users_status CHECK (status IN ('active', 'disabled'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =========================================================
-- 2. classes 班级表
-- =========================================================

CREATE TABLE classes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '班级ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '创建班级的教师ID',
  class_name VARCHAR(100) NOT NULL COMMENT '班级名称',
  grade VARCHAR(20) NULL COMMENT '年级',
  invite_code VARCHAR(20) NOT NULL COMMENT '班级邀请码',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '班级状态：active / archived',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_classes_invite_code (invite_code),
  KEY idx_classes_teacher_id (teacher_id),
  KEY idx_classes_status (status),
  CONSTRAINT fk_classes_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_classes_status CHECK (status IN ('active', 'archived'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';

-- =========================================================
-- 3. class_members 班级成员表
-- =========================================================

CREATE TABLE class_members (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  class_id BIGINT UNSIGNED NOT NULL COMMENT '班级ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT '学生用户ID',
  member_role VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT '班级内角色：student',
  joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '成员状态：active / removed',
  PRIMARY KEY (id),
  UNIQUE KEY uk_class_members_class_user (class_id, user_id),
  KEY idx_class_members_user_id (user_id),
  KEY idx_class_members_status (status),
  CONSTRAINT fk_class_members_class
    FOREIGN KEY (class_id) REFERENCES classes(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_class_members_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_class_members_role CHECK (member_role IN ('student')),
  CONSTRAINT chk_class_members_status CHECK (status IN ('active', 'removed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级成员表';

-- =========================================================
-- 4. lesson_plans 教案表
-- =========================================================

CREATE TABLE lesson_plans (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '教案ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '上传教师ID',
  title VARCHAR(200) NOT NULL COMMENT '教案标题',
  grade VARCHAR(20) NULL COMMENT '年级',
  subject VARCHAR(50) NOT NULL DEFAULT 'music' COMMENT '学科，默认 music',
  original_file_url VARCHAR(500) NULL COMMENT '原始教案文件地址',
  raw_text MEDIUMTEXT NULL COMMENT '提取出的教案文本',
  parsed_json JSON NULL COMMENT '结构化解析结果',
  parse_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '解析状态：pending / success / failed',
  parse_error TEXT NULL COMMENT '解析失败原因',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_lesson_plans_teacher_id (teacher_id),
  KEY idx_lesson_plans_parse_status (parse_status),
  KEY idx_lesson_plans_created_at (created_at),
  CONSTRAINT fk_lesson_plans_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_lesson_plans_parse_status CHECK (parse_status IN ('pending', 'success', 'failed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教案表';

-- =========================================================
-- 5. component_definitions 组件定义表
-- =========================================================

CREATE TABLE component_definitions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '组件ID',
  component_code VARCHAR(100) NOT NULL COMMENT '组件编码',
  component_name VARCHAR(100) NOT NULL COMMENT '组件名称',
  category VARCHAR(50) NOT NULL COMMENT '组件类别：music_basic / instrument / interactive / flow / control / telemetry',
  description TEXT NULL COMMENT '组件说明',
  supported_grades_json JSON NULL COMMENT '支持年级',
  music_elements_json JSON NULL COMMENT '支持音乐要素',
  student_behaviors_json JSON NULL COMMENT '支持学生行为',
  input_schema_json JSON NOT NULL COMMENT '输入参数规范',
  output_schema_json JSON NOT NULL COMMENT '输出结果规范',
  configurable_params_json JSON NULL COMMENT '可配置参数',
  boundary_json JSON NULL COMMENT '能力边界',
  version VARCHAR(20) NOT NULL DEFAULT '1.0.0' COMMENT '组件版本',
  enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_component_definitions_code (component_code),
  KEY idx_component_definitions_category (category),
  KEY idx_component_definitions_enabled (enabled),
  CONSTRAINT chk_component_definitions_category CHECK (
    category IN ('music_basic', 'instrument', 'interactive', 'flow', 'control', 'telemetry')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='组件定义表';

-- =========================================================
-- 6. interactive_packages 互动包表
-- current_version_id 在 package_versions 创建后补充外键
-- =========================================================

CREATE TABLE interactive_packages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '互动包ID',
  lesson_plan_id BIGINT UNSIGNED NOT NULL COMMENT '来源教案ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '创建教师ID',
  package_title VARCHAR(200) NOT NULL COMMENT '互动包名称',
  description TEXT NULL COMMENT '互动包简介',
  current_version_id BIGINT UNSIGNED NULL COMMENT '当前版本ID',
  status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '互动包状态：draft / confirmed / published / archived',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_interactive_packages_lesson_plan_id (lesson_plan_id),
  KEY idx_interactive_packages_teacher_id (teacher_id),
  KEY idx_interactive_packages_current_version_id (current_version_id),
  KEY idx_interactive_packages_status (status),
  CONSTRAINT fk_interactive_packages_lesson_plan
    FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_interactive_packages_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_interactive_packages_status CHECK (status IN ('draft', 'confirmed', 'published', 'archived'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='互动包表';

-- =========================================================
-- 7. package_versions 作品包版本表
-- =========================================================

CREATE TABLE package_versions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '版本ID',
  package_id BIGINT UNSIGNED NOT NULL COMMENT '互动包ID',
  parent_version_id BIGINT UNSIGNED NULL COMMENT '父版本ID，用于二次修改追溯',
  version_no INT NOT NULL COMMENT '版本号',
  version_name VARCHAR(100) NULL COMMENT '版本名称',
  version_type VARCHAR(30) NOT NULL DEFAULT 'initial' COMMENT '版本类型：initial / modified / confirmed / published',
  version_note VARCHAR(255) NULL COMMENT '版本说明',
  activity_chain_json JSON NOT NULL COMMENT '活动链完整结构',
  teacher_control_json JSON NULL COMMENT '教师控制配置',
  student_runtime_json JSON NULL COMMENT '学生端运行配置',
  telemetry_config_json JSON NULL COMMENT '数据采集配置',
  status VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '版本状态：draft / confirmed / locked / archived',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_package_versions_package_no (package_id, version_no),
  KEY idx_package_versions_package_id (package_id),
  KEY idx_package_versions_parent_version_id (parent_version_id),
  KEY idx_package_versions_status (status),
  CONSTRAINT fk_package_versions_package
    FOREIGN KEY (package_id) REFERENCES interactive_packages(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_package_versions_parent
    FOREIGN KEY (parent_version_id) REFERENCES package_versions(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_package_versions_type CHECK (version_type IN ('initial', 'modified', 'confirmed', 'published')),
  CONSTRAINT chk_package_versions_status CHECK (status IN ('draft', 'confirmed', 'locked', 'archived'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品包版本表';

ALTER TABLE interactive_packages
  ADD CONSTRAINT fk_interactive_packages_current_version
  FOREIGN KEY (current_version_id) REFERENCES package_versions(id)
  ON DELETE SET NULL ON UPDATE CASCADE;

-- =========================================================
-- 8. generation_jobs 生成任务表
-- =========================================================

CREATE TABLE generation_jobs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '生成任务ID',
  lesson_plan_id BIGINT UNSIGNED NOT NULL COMMENT '教案ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '教师ID',
  job_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending / running / success / failed',
  progress INT NOT NULL DEFAULT 0 COMMENT '生成进度：0-100',
  preferences_json JSON NULL COMMENT '教师生成偏好',
  result_package_id BIGINT UNSIGNED NULL COMMENT '生成成功后的互动包ID',
  error_message TEXT NULL COMMENT '失败原因',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_generation_jobs_lesson_plan_id (lesson_plan_id),
  KEY idx_generation_jobs_teacher_id (teacher_id),
  KEY idx_generation_jobs_result_package_id (result_package_id),
  KEY idx_generation_jobs_status (job_status),
  CONSTRAINT fk_generation_jobs_lesson_plan
    FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_generation_jobs_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_generation_jobs_result_package
    FOREIGN KEY (result_package_id) REFERENCES interactive_packages(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_generation_jobs_status CHECK (job_status IN ('pending', 'running', 'success', 'failed')),
  CONSTRAINT chk_generation_jobs_progress CHECK (progress BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生成任务表';

-- =========================================================
-- 9. proposal_cards 方案卡表
-- =========================================================

CREATE TABLE proposal_cards (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '方案卡ID',
  package_version_id BIGINT UNSIGNED NOT NULL COMMENT '作品版本ID',
  summary TEXT NOT NULL COMMENT '方案摘要',
  node_count INT NOT NULL COMMENT '活动节点数量',
  proposal_json JSON NOT NULL COMMENT '方案卡详细内容',
  confirm_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '确认状态：pending / confirmed / rejected',
  teacher_feedback TEXT NULL COMMENT '教师修改意见',
  confirmed_at DATETIME NULL COMMENT '确认时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_proposal_cards_package_version_id (package_version_id),
  KEY idx_proposal_cards_confirm_status (confirm_status),
  CONSTRAINT fk_proposal_cards_package_version
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_proposal_cards_confirm_status CHECK (confirm_status IN ('pending', 'confirmed', 'rejected'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='方案卡表';

-- =========================================================
-- 10. activity_nodes 活动节点表
-- =========================================================

CREATE TABLE activity_nodes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '活动节点ID',
  package_version_id BIGINT UNSIGNED NOT NULL COMMENT '作品版本ID',
  node_code VARCHAR(100) NOT NULL COMMENT '节点编码',
  node_title VARCHAR(200) NOT NULL COMMENT '节点标题',
  node_type VARCHAR(50) NOT NULL COMMENT '节点类型：entry / tool / game / creation / summary',
  order_no INT NOT NULL COMMENT '节点顺序',
  source_lesson_step VARCHAR(200) NULL COMMENT '来源教案环节',
  target_objective TEXT NULL COMMENT '服务教学目标',
  estimated_minutes INT NULL COMMENT '预计耗时',
  node_config_json JSON NOT NULL COMMENT '节点运行配置',
  unlock_required BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否需要教师解锁',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_activity_nodes_version_code (package_version_id, node_code),
  KEY idx_activity_nodes_package_version_id (package_version_id),
  KEY idx_activity_nodes_node_type (node_type),
  KEY idx_activity_nodes_order_no (order_no),
  CONSTRAINT fk_activity_nodes_package_version
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_activity_nodes_type CHECK (node_type IN ('entry', 'tool', 'game', 'creation', 'summary')),
  CONSTRAINT chk_activity_nodes_estimated_minutes CHECK (estimated_minutes IS NULL OR estimated_minutes >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动节点表';

-- =========================================================
-- 11. component_instances 组件实例表
-- =========================================================

CREATE TABLE component_instances (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '组件实例ID',
  activity_node_id BIGINT UNSIGNED NOT NULL COMMENT '活动节点ID',
  component_definition_id BIGINT UNSIGNED NOT NULL COMMENT '组件定义ID',
  instance_name VARCHAR(100) NULL COMMENT '实例名称',
  instance_config_json JSON NOT NULL COMMENT '实例配置',
  order_no INT NOT NULL DEFAULT 1 COMMENT '组件顺序',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_component_instances_activity_node_id (activity_node_id),
  KEY idx_component_instances_definition_id (component_definition_id),
  KEY idx_component_instances_order_no (order_no),
  CONSTRAINT fk_component_instances_activity_node
    FOREIGN KEY (activity_node_id) REFERENCES activity_nodes(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_component_instances_definition
    FOREIGN KEY (component_definition_id) REFERENCES component_definitions(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_component_instances_order_no CHECK (order_no > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='组件实例表';

-- =========================================================
-- 12. assets 素材表
-- =========================================================

CREATE TABLE assets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '素材ID',
  package_version_id BIGINT UNSIGNED NOT NULL COMMENT '作品版本ID',
  activity_node_id BIGINT UNSIGNED NULL COMMENT '所属活动节点ID，可为空',
  asset_type VARCHAR(50) NOT NULL COMMENT '素材类型：scene / character / prop / reward / audio / instrument_image',
  asset_name VARCHAR(100) NOT NULL COMMENT '素材名称',
  file_url VARCHAR(500) NOT NULL COMMENT '文件地址',
  source_type VARCHAR(50) NOT NULL COMMENT '素材来源：generated / material_library / uploaded',
  is_traceable BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否可追溯',
  license_info VARCHAR(255) NULL COMMENT '授权信息',
  metadata_json JSON NULL COMMENT '素材元信息',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_assets_package_version_id (package_version_id),
  KEY idx_assets_activity_node_id (activity_node_id),
  KEY idx_assets_asset_type (asset_type),
  KEY idx_assets_source_type (source_type),
  CONSTRAINT fk_assets_package_version
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_assets_activity_node
    FOREIGN KEY (activity_node_id) REFERENCES activity_nodes(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_assets_asset_type CHECK (
    asset_type IN ('scene', 'character', 'prop', 'reward', 'audio', 'instrument_image')
  ),
  CONSTRAINT chk_assets_source_type CHECK (source_type IN ('generated', 'material_library', 'uploaded'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='素材表';

-- =========================================================
-- 13. quality_reports 质量检查表
-- =========================================================

CREATE TABLE quality_reports (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '检查报告ID',
  package_version_id BIGINT UNSIGNED NOT NULL COMMENT '作品版本ID',
  overall_status VARCHAR(20) NOT NULL COMMENT '总体状态：pass / warning / failed',
  score INT NOT NULL COMMENT '质量评分',
  lesson_match_result VARCHAR(20) NOT NULL COMMENT '教案贴合检查结果',
  music_logic_result VARCHAR(20) NOT NULL COMMENT '音乐逻辑检查结果',
  component_result VARCHAR(20) NOT NULL COMMENT '组件调用检查结果',
  asset_result VARCHAR(20) NOT NULL COMMENT '素材检查结果',
  classroom_control_result VARCHAR(20) NOT NULL COMMENT '课堂控制检查结果',
  student_runtime_result VARCHAR(20) NOT NULL COMMENT '学生端可用性检查结果',
  telemetry_result VARCHAR(20) NOT NULL COMMENT '数据记录检查结果',
  detail_json JSON NOT NULL COMMENT '详细检查结果',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_quality_reports_package_version_id (package_version_id),
  KEY idx_quality_reports_overall_status (overall_status),
  CONSTRAINT fk_quality_reports_package_version
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_quality_reports_overall_status CHECK (overall_status IN ('pass', 'warning', 'failed')),
  CONSTRAINT chk_quality_reports_score CHECK (score BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='质量检查表';

-- =========================================================
-- 14. package_publications 发布表
-- =========================================================

CREATE TABLE package_publications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '发布ID',
  package_id BIGINT UNSIGNED NOT NULL COMMENT '互动包ID',
  package_version_id BIGINT UNSIGNED NOT NULL COMMENT '发布版本ID',
  class_id BIGINT UNSIGNED NOT NULL COMMENT '发布到的班级ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '发布教师ID',
  publish_status VARCHAR(20) NOT NULL DEFAULT 'published' COMMENT '发布状态：published / revoked',
  review_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否允许课后复习',
  published_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_package_publications_package_id (package_id),
  KEY idx_package_publications_version_id (package_version_id),
  KEY idx_package_publications_class_id (class_id),
  KEY idx_package_publications_teacher_id (teacher_id),
  KEY idx_package_publications_status (publish_status),
  CONSTRAINT fk_package_publications_package
    FOREIGN KEY (package_id) REFERENCES interactive_packages(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_package_publications_version
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_package_publications_class
    FOREIGN KEY (class_id) REFERENCES classes(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_package_publications_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_package_publications_status CHECK (publish_status IN ('published', 'revoked'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='发布表';

-- =========================================================
-- 15. classroom_sessions 课堂会话表
-- =========================================================

CREATE TABLE classroom_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '课堂会话ID',
  publication_id BIGINT UNSIGNED NOT NULL COMMENT '发布ID',
  class_id BIGINT UNSIGNED NOT NULL COMMENT '班级ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '教师ID',
  current_node_id BIGINT UNSIGNED NULL COMMENT '当前活动节点ID',
  session_status VARCHAR(20) NOT NULL DEFAULT 'not_started' COMMENT '课堂状态：not_started / running / paused / ended',
  started_at DATETIME NULL COMMENT '开始时间',
  ended_at DATETIME NULL COMMENT '结束时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_classroom_sessions_publication_id (publication_id),
  KEY idx_classroom_sessions_class_id (class_id),
  KEY idx_classroom_sessions_teacher_id (teacher_id),
  KEY idx_classroom_sessions_current_node_id (current_node_id),
  KEY idx_classroom_sessions_status (session_status),
  CONSTRAINT fk_classroom_sessions_publication
    FOREIGN KEY (publication_id) REFERENCES package_publications(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_classroom_sessions_class
    FOREIGN KEY (class_id) REFERENCES classes(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_classroom_sessions_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_classroom_sessions_current_node
    FOREIGN KEY (current_node_id) REFERENCES activity_nodes(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_classroom_sessions_status CHECK (session_status IN ('not_started', 'running', 'paused', 'ended'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课堂会话表';

-- =========================================================
-- 16. session_node_states 课堂节点状态表
-- =========================================================

CREATE TABLE session_node_states (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '课堂会话ID',
  activity_node_id BIGINT UNSIGNED NOT NULL COMMENT '活动节点ID',
  lock_status VARCHAR(20) NOT NULL DEFAULT 'locked' COMMENT '节点锁定状态：locked / unlocked',
  unlocked_at DATETIME NULL COMMENT '解锁时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_session_node_states_session_node (session_id, activity_node_id),
  KEY idx_session_node_states_activity_node_id (activity_node_id),
  KEY idx_session_node_states_lock_status (lock_status),
  CONSTRAINT fk_session_node_states_session
    FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_session_node_states_activity_node
    FOREIGN KEY (activity_node_id) REFERENCES activity_nodes(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_session_node_states_lock_status CHECK (lock_status IN ('locked', 'unlocked'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课堂节点状态表';

-- =========================================================
-- 17. student_progress 学生进度表
-- =========================================================

CREATE TABLE student_progress (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '课堂会话ID',
  student_id BIGINT UNSIGNED NOT NULL COMMENT '学生ID',
  activity_node_id BIGINT UNSIGNED NOT NULL COMMENT '活动节点ID',
  progress_status VARCHAR(20) NOT NULL DEFAULT 'not_started' COMMENT '进度状态：not_started / doing / completed',
  score DECIMAL(5,2) NULL COMMENT '得分',
  attempt_count INT NOT NULL DEFAULT 0 COMMENT '尝试次数',
  wrong_count INT NOT NULL DEFAULT 0 COMMENT '错误次数',
  hint_used_count INT NOT NULL DEFAULT 0 COMMENT '使用提示次数',
  duration_seconds INT NOT NULL DEFAULT 0 COMMENT '用时，单位秒',
  result_json JSON NULL COMMENT '学生结果',
  started_at DATETIME NULL COMMENT '开始时间',
  completed_at DATETIME NULL COMMENT '完成时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_student_progress_session_student_node (session_id, student_id, activity_node_id),
  KEY idx_student_progress_student_id (student_id),
  KEY idx_student_progress_activity_node_id (activity_node_id),
  KEY idx_student_progress_status (progress_status),
  CONSTRAINT fk_student_progress_session
    FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_student_progress_student
    FOREIGN KEY (student_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_student_progress_activity_node
    FOREIGN KEY (activity_node_id) REFERENCES activity_nodes(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_student_progress_status CHECK (progress_status IN ('not_started', 'doing', 'completed')),
  CONSTRAINT chk_student_progress_score CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
  CONSTRAINT chk_student_progress_counts CHECK (
    attempt_count >= 0 AND wrong_count >= 0 AND hint_used_count >= 0 AND duration_seconds >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生进度表';

-- =========================================================
-- 18. learning_events 学习事件表
-- =========================================================

CREATE TABLE learning_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '事件ID',
  session_id BIGINT UNSIGNED NOT NULL COMMENT '课堂会话ID',
  student_id BIGINT UNSIGNED NOT NULL COMMENT '学生ID',
  activity_node_id BIGINT UNSIGNED NULL COMMENT '活动节点ID',
  event_type VARCHAR(100) NOT NULL COMMENT '事件类型',
  event_payload_json JSON NULL COMMENT '事件内容',
  client_time DATETIME NULL COMMENT '客户端时间',
  server_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '服务端接收时间',
  PRIMARY KEY (id),
  KEY idx_learning_events_session_id (session_id),
  KEY idx_learning_events_student_id (student_id),
  KEY idx_learning_events_activity_node_id (activity_node_id),
  KEY idx_learning_events_event_type (event_type),
  KEY idx_learning_events_server_time (server_time),
  CONSTRAINT fk_learning_events_session
    FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_learning_events_student
    FOREIGN KEY (student_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_learning_events_activity_node
    FOREIGN KEY (activity_node_id) REFERENCES activity_nodes(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习事件表';

-- =========================================================
-- 19. package_modify_records 作品包修改记录表
-- =========================================================

CREATE TABLE package_modify_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '修改记录ID',
  package_id BIGINT UNSIGNED NOT NULL COMMENT '互动包ID',
  old_version_id BIGINT UNSIGNED NOT NULL COMMENT '修改前版本ID',
  new_version_id BIGINT UNSIGNED NULL COMMENT '修改后版本ID',
  teacher_id BIGINT UNSIGNED NOT NULL COMMENT '操作教师ID',
  modify_scope VARCHAR(50) NOT NULL COMMENT '修改范围：node_config / component_param / asset / activity_chain / package_setting',
  target_type VARCHAR(50) NOT NULL COMMENT '修改对象类型：package / activity_node / component_instance / asset',
  target_id BIGINT UNSIGNED NULL COMMENT '修改对象ID',
  modify_instruction TEXT NOT NULL COMMENT '教师修改指令',
  modify_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '修改状态：pending / success / failed',
  change_summary TEXT NULL COMMENT '修改摘要',
  error_message TEXT NULL COMMENT '修改失败原因',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_package_modify_records_package_id (package_id),
  KEY idx_package_modify_records_old_version_id (old_version_id),
  KEY idx_package_modify_records_new_version_id (new_version_id),
  KEY idx_package_modify_records_teacher_id (teacher_id),
  KEY idx_package_modify_records_status (modify_status),
  KEY idx_package_modify_records_scope (modify_scope),
  CONSTRAINT fk_package_modify_records_package
    FOREIGN KEY (package_id) REFERENCES interactive_packages(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_package_modify_records_old_version
    FOREIGN KEY (old_version_id) REFERENCES package_versions(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_package_modify_records_new_version
    FOREIGN KEY (new_version_id) REFERENCES package_versions(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_package_modify_records_teacher
    FOREIGN KEY (teacher_id) REFERENCES users(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT chk_package_modify_records_scope CHECK (
    modify_scope IN ('node_config', 'component_param', 'asset', 'activity_chain', 'package_setting')
  ),
  CONSTRAINT chk_package_modify_records_target_type CHECK (
    target_type IN ('package', 'activity_node', 'component_instance', 'asset')
  ),
  CONSTRAINT chk_package_modify_records_status CHECK (modify_status IN ('pending', 'success', 'failed'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品包修改记录表';

-- =========================================================
-- 20. package_version_diffs 版本差异表
-- 用于记录二次修改时具体字段从 old_value 变为 new_value
-- =========================================================

CREATE TABLE package_version_diffs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '差异ID',
  modify_record_id BIGINT UNSIGNED NOT NULL COMMENT '修改记录ID',
  package_id BIGINT UNSIGNED NOT NULL COMMENT '互动包ID',
  old_version_id BIGINT UNSIGNED NOT NULL COMMENT '旧版本ID',
  new_version_id BIGINT UNSIGNED NOT NULL COMMENT '新版本ID',
  object_type VARCHAR(50) NOT NULL COMMENT '变化对象类型：package / activity_node / component_instance / asset',
  object_id BIGINT UNSIGNED NULL COMMENT '变化对象ID',
  field_path VARCHAR(255) NOT NULL COMMENT '变化字段路径，如 node_config_json.difficulty',
  old_value TEXT NULL COMMENT '旧值',
  new_value TEXT NULL COMMENT '新值',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_package_version_diffs_modify_record_id (modify_record_id),
  KEY idx_package_version_diffs_package_id (package_id),
  KEY idx_package_version_diffs_old_version_id (old_version_id),
  KEY idx_package_version_diffs_new_version_id (new_version_id),
  KEY idx_package_version_diffs_object (object_type, object_id),
  CONSTRAINT fk_package_version_diffs_modify_record
    FOREIGN KEY (modify_record_id) REFERENCES package_modify_records(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_package_version_diffs_package
    FOREIGN KEY (package_id) REFERENCES interactive_packages(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_package_version_diffs_old_version
    FOREIGN KEY (old_version_id) REFERENCES package_versions(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_package_version_diffs_new_version
    FOREIGN KEY (new_version_id) REFERENCES package_versions(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_package_version_diffs_object_type CHECK (
    object_type IN ('package', 'activity_node', 'component_instance', 'asset')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='版本差异表';

-- =========================================================
-- 21. 常用初始化组件数据
-- 如只需要建表，可删除本段 INSERT。
-- =========================================================

INSERT INTO component_definitions
(component_code, component_name, category, description, supported_grades_json, music_elements_json, student_behaviors_json, input_schema_json, output_schema_json, configurable_params_json, boundary_json, version, enabled, created_at, updated_at)
VALUES
('scene_display', '课堂场景展示组件', 'flow', '展示本课主题场景图',
 JSON_ARRAY('1','2','3','4','5','6'), JSON_ARRAY('scene'), JSON_ARRAY('view'),
 JSON_OBJECT(), JSON_OBJECT(), JSON_OBJECT(),
 JSON_ARRAY('只负责展示场景，不负责音乐判断'), '1.0.0', TRUE, NOW(), NOW()),

('lesson_title_card', '课程标题卡组件', 'flow', '展示课程名称和课堂目标',
 JSON_ARRAY('1','2','3','4','5','6'), JSON_ARRAY('lesson_intro'), JSON_ARRAY('view'),
 JSON_OBJECT(), JSON_OBJECT(), JSON_OBJECT(),
 JSON_ARRAY('只负责文本展示'), '1.0.0', TRUE, NOW(), NOW()),

('meter_compare', '节拍对比工具', 'music_basic', '用于 2/4、3/4 等节拍对比',
 JSON_ARRAY('3','4','5','6'), JSON_ARRAY('meter','beat','strong_weak'), JSON_ARRAY('tap','compare'),
 JSON_OBJECT('meters', JSON_ARRAY('2/4','3/4')),
 JSON_OBJECT('selectedMeter', 'string', 'isCorrect', 'boolean'),
 JSON_OBJECT('difficulty', JSON_ARRAY('easy','normal','hard'), 'hintEnabled', true),
 JSON_ARRAY('只支持常见拍号', '不负责完整乐曲播放'), '1.0.0', TRUE, NOW(), NOW()),

('beat_feedback', '拍击反馈组件', 'interactive', '学生拍击后给出节拍反馈',
 JSON_ARRAY('3','4','5','6'), JSON_ARRAY('beat','tempo'), JSON_ARRAY('tap'),
 JSON_OBJECT(), JSON_OBJECT('isCorrect', 'boolean', 'attemptCount', 'number'),
 JSON_OBJECT('hintEnabled', true, 'tempo', 90),
 JSON_ARRAY('不负责完整乐曲播放', '只记录局部拍击反馈'), '1.0.0', TRUE, NOW(), NOW()),

('rhythm_drag_game', '节奏拖拽游戏', 'interactive', '学生拖拽节奏卡完成排序',
 JSON_ARRAY('3','4','5','6'), JSON_ARRAY('rhythm','meter'), JSON_ARRAY('drag','sort','submit'),
 JSON_OBJECT('rhythmCards', 'array', 'meter', 'string'),
 JSON_OBJECT('isCorrect', 'boolean', 'wrongCount', 'number'),
 JSON_OBJECT('rhythmCardCount', 8, 'difficulty', 'normal', 'hintEnabled', true),
 JSON_ARRAY('节奏卡总时值必须满足拍号', '不生成超出组件边界的节奏型'), '1.0.0', TRUE, NOW(), NOW()),

('creation_panel', '创编工作坊组件', 'interactive', '学生进行节奏或旋律创编',
 JSON_ARRAY('3','4','5','6'), JSON_ARRAY('rhythm','melody','creation'), JSON_ARRAY('create','preview','submit'),
 JSON_OBJECT('constraints', 'object'),
 JSON_OBJECT('creationResult', 'object'),
 JSON_OBJECT('groupMode', false, 'previewAudio', true),
 JSON_ARRAY('创编必须有约束条件', '创编结果应支持课堂回扣'), '1.0.0', TRUE, NOW(), NOW()),

('summary_page', '展示总结页组件', 'flow', '用于课堂总结和成果展示',
 JSON_ARRAY('1','2','3','4','5','6'), JSON_ARRAY('summary'), JSON_ARRAY('view'),
 JSON_OBJECT(), JSON_OBJECT(), JSON_OBJECT(),
 JSON_ARRAY('只负责总结展示'), '1.0.0', TRUE, NOW(), NOW());

-- =========================================================
-- 22. 常用查询视图：可选
-- =========================================================

CREATE OR REPLACE VIEW v_package_latest_versions AS
SELECT
  p.id AS package_id,
  p.package_title,
  p.teacher_id,
  p.status AS package_status,
  v.id AS version_id,
  v.version_no,
  v.version_name,
  v.status AS version_status,
  v.created_at AS version_created_at
FROM interactive_packages p
LEFT JOIN package_versions v ON p.current_version_id = v.id;

CREATE OR REPLACE VIEW v_classroom_student_progress AS
SELECT
  cs.id AS session_id,
  cs.class_id,
  c.class_name,
  sp.student_id,
  u.real_name AS student_name,
  sp.activity_node_id,
  an.node_title,
  sp.progress_status,
  sp.score,
  sp.attempt_count,
  sp.wrong_count,
  sp.hint_used_count,
  sp.duration_seconds,
  sp.completed_at
FROM student_progress sp
JOIN classroom_sessions cs ON sp.session_id = cs.id
JOIN classes c ON cs.class_id = c.id
JOIN users u ON sp.student_id = u.id
JOIN activity_nodes an ON sp.activity_node_id = an.id;

-- =========================================================
-- 完成
-- =========================================================
