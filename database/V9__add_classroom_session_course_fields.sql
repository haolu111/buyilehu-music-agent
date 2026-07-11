ALTER TABLE classroom_sessions
  ADD COLUMN course_title VARCHAR(150) NULL AFTER status,
  ADD COLUMN course_description TEXT NULL AFTER course_title,
  ADD COLUMN scheduled_start_at DATETIME NULL AFTER course_description;