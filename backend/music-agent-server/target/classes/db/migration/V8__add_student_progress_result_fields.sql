ALTER TABLE student_progress ADD COLUMN progress_status VARCHAR(30) NOT NULL DEFAULT 'not_started';
ALTER TABLE student_progress ADD COLUMN wrong_count INT NOT NULL DEFAULT 0;
ALTER TABLE student_progress ADD COLUMN hint_used_count INT NOT NULL DEFAULT 0;
ALTER TABLE student_progress ADD COLUMN duration_seconds INT NOT NULL DEFAULT 0;
ALTER TABLE student_progress ADD COLUMN result_json TEXT NULL;
