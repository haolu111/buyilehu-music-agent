ALTER TABLE lesson_plans ADD COLUMN raw_text TEXT NULL;
ALTER TABLE lesson_plans ADD COLUMN parsed_json TEXT NULL;
ALTER TABLE lesson_plans ADD COLUMN parse_status VARCHAR(20) NOT NULL DEFAULT 'pending';
