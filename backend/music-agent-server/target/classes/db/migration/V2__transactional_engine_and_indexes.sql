ALTER TABLE activity_nodes ENGINE=InnoDB;
ALTER TABLE assets ENGINE=InnoDB;
ALTER TABLE class_members ENGINE=InnoDB;
ALTER TABLE classes ENGINE=InnoDB;
ALTER TABLE classroom_sessions ENGINE=InnoDB;
ALTER TABLE component_definitions ENGINE=InnoDB;
ALTER TABLE component_instances ENGINE=InnoDB;
ALTER TABLE generation_jobs ENGINE=InnoDB;
ALTER TABLE interactive_packages ENGINE=InnoDB;
ALTER TABLE learning_events ENGINE=InnoDB;
ALTER TABLE lesson_plans ENGINE=InnoDB;
ALTER TABLE package_modify_records ENGINE=InnoDB;
ALTER TABLE package_publications ENGINE=InnoDB;
ALTER TABLE package_version_diffs ENGINE=InnoDB;
ALTER TABLE package_versions ENGINE=InnoDB;
ALTER TABLE proposal_cards ENGINE=InnoDB;
ALTER TABLE quality_reports ENGINE=InnoDB;
ALTER TABLE session_node_states ENGINE=InnoDB;
ALTER TABLE student_progress ENGINE=InnoDB;
ALTER TABLE users ENGINE=InnoDB;

ALTER TABLE component_definitions
    ADD CONSTRAINT uk_component_definitions_key UNIQUE (component_key);
ALTER TABLE class_members
    ADD CONSTRAINT uk_class_members_class_user UNIQUE (class_id, user_id);
ALTER TABLE package_versions
    ADD CONSTRAINT uk_package_versions_package_no UNIQUE (package_id, version_no);
ALTER TABLE session_node_states
    ADD CONSTRAINT uk_session_node_states_session_node UNIQUE (session_id, activity_node_id);

CREATE INDEX idx_activity_nodes_package_sort ON activity_nodes (package_id, sort_order);
CREATE INDEX idx_assets_package ON assets (package_id);
CREATE INDEX idx_class_members_user_status ON class_members (user_id, status);
CREATE INDEX idx_classes_teacher_status ON classes (teacher_id, status);
CREATE INDEX idx_classroom_sessions_class_status ON classroom_sessions (class_id, status);
CREATE INDEX idx_classroom_sessions_teacher_status ON classroom_sessions (teacher_id, status);
CREATE INDEX idx_component_instances_node_sort ON component_instances (activity_node_id, sort_order);
CREATE INDEX idx_generation_jobs_creator_status ON generation_jobs (created_by, status);
CREATE INDEX idx_generation_jobs_lesson ON generation_jobs (lesson_plan_id);
CREATE UNIQUE INDEX uk_interactive_packages_generation_job ON interactive_packages (generation_job_id);
CREATE INDEX idx_interactive_packages_owner ON interactive_packages (owner_id, id);
CREATE INDEX idx_learning_events_session_time ON learning_events (session_id, occurred_at);
CREATE INDEX idx_learning_events_student ON learning_events (student_id, occurred_at);
CREATE INDEX idx_lesson_plans_teacher ON lesson_plans (teacher_id, id);
CREATE INDEX idx_package_modify_records_package ON package_modify_records (package_id, id);
CREATE INDEX idx_package_publications_package ON package_publications (package_id, id);
CREATE INDEX idx_package_version_diffs_package ON package_version_diffs (package_id, id);
CREATE INDEX idx_proposal_cards_package ON proposal_cards (package_id, id);
CREATE INDEX idx_quality_reports_package ON quality_reports (package_id, id);
CREATE INDEX idx_student_progress_session_student ON student_progress (session_id, student_id);
