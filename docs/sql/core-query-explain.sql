SET @owner_id = 1;
SET @package_id = 1;
SET @activity_node_id = 1;
SET @creator_id = 1;

EXPLAIN FORMAT=JSON
SELECT *
FROM interactive_packages
WHERE owner_id = @owner_id
ORDER BY id DESC;

EXPLAIN FORMAT=JSON
SELECT *
FROM activity_nodes
WHERE package_id = @package_id
ORDER BY sort_order ASC;

EXPLAIN FORMAT=JSON
SELECT *
FROM component_instances
WHERE activity_node_id = @activity_node_id
ORDER BY sort_order ASC;

EXPLAIN FORMAT=JSON
SELECT *
FROM generation_jobs
WHERE created_by = @creator_id
  AND status = 'queued';

EXPLAIN FORMAT=JSON
SELECT *
FROM outbox_events
WHERE status = 'pending'
  AND next_attempt_at <= NOW()
ORDER BY id
LIMIT 20;
