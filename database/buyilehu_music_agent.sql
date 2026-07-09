/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : buyilehu_music_agent

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 09/07/2026 16:15:36
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for activity_nodes
-- ----------------------------
DROP TABLE IF EXISTS `activity_nodes`;
CREATE TABLE `activity_nodes`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `parent_node_id` bigint(20) NULL DEFAULT NULL,
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `node_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0,
  `config_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of activity_nodes
-- ----------------------------
INSERT INTO `activity_nodes` VALUES (1, 1, NULL, '课堂入口页', 'entry', 1, '{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `activity_nodes` VALUES (2, 1, NULL, '节拍体验工具', 'meter_experience', 2, '{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `activity_nodes` VALUES (3, 1, NULL, '节奏拖拽游戏', 'rhythm_game', 3, '{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `activity_nodes` VALUES (4, 1, NULL, '创编工作坊', 'creation_workshop', 4, '{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `activity_nodes` VALUES (5, 1, NULL, '展示总结页', 'summary', 5, '{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `activity_nodes` VALUES (6, 2, NULL, '课堂入口页', 'entry', 1, '{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `activity_nodes` VALUES (7, 2, NULL, '节拍体验工具', 'meter_experience', 2, '{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `activity_nodes` VALUES (8, 2, NULL, '节奏拖拽游戏', 'rhythm_game', 3, '{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `activity_nodes` VALUES (9, 2, NULL, '创编工作坊', 'creation_workshop', 4, '{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"],\"description\":\"\",\"difficulty\":\"normal\",\"rhythmCardCount\":4,\"hintEnabled\":true,\"hidden\":false}', '2026-07-09 13:16:55', '2026-07-09 13:43:25');
INSERT INTO `activity_nodes` VALUES (10, 2, NULL, '展示总结页', 'summary', 5, '{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');

-- ----------------------------
-- Table structure for assets
-- ----------------------------
DROP TABLE IF EXISTS `assets`;
CREATE TABLE `assets`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `owner_id` bigint(20) NULL DEFAULT NULL,
  `package_id` bigint(20) NULL DEFAULT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mime_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `file_size` bigint(20) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of assets
-- ----------------------------
INSERT INTO `assets` VALUES (1, 1, 1, 'placeholder', 'package-cover-placeholder.png', 'assets/placeholders/package-cover-placeholder.png', 'image/png', 0, '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `assets` VALUES (2, 1, 2, 'placeholder', 'package-cover-placeholder.png', 'assets/placeholders/package-cover-placeholder.png', 'image/png', 0, '2026-07-09 13:16:55', '2026-07-09 13:16:55');

-- ----------------------------
-- Table structure for class_members
-- ----------------------------
DROP TABLE IF EXISTS `class_members`;
CREATE TABLE `class_members`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `class_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of class_members
-- ----------------------------
INSERT INTO `class_members` VALUES (1, 1, 2, 'student', 'active', '2026-07-06 16:44:40', '2026-07-06 16:44:40');

-- ----------------------------
-- Table structure for classes
-- ----------------------------
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `class_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_id` bigint(20) NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `invite_code` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_classes_invite_code`(`invite_code`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES (1, '一年级一班', 1, '无', 'active', '2026-07-06 16:43:56', '2026-07-06 16:43:56', '4TKNUXHR');

-- ----------------------------
-- Table structure for classroom_sessions
-- ----------------------------
DROP TABLE IF EXISTS `classroom_sessions`;
CREATE TABLE `classroom_sessions`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `class_id` bigint(20) NOT NULL,
  `package_id` bigint(20) NOT NULL,
  `teacher_id` bigint(20) NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'not_started',
  `started_at` datetime(0) NULL DEFAULT NULL,
  `ended_at` datetime(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `publication_id` bigint(20) NULL DEFAULT NULL,
  `current_node_id` bigint(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_classroom_sessions_publication_id`(`publication_id`) USING BTREE,
  INDEX `idx_classroom_sessions_current_node_id`(`current_node_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classroom_sessions
-- ----------------------------

-- ----------------------------
-- Table structure for component_definitions
-- ----------------------------
DROP TABLE IF EXISTS `component_definitions`;
CREATE TABLE `component_definitions`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `component_key` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `schema_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of component_definitions
-- ----------------------------
INSERT INTO `component_definitions` VALUES (1, 'scene_display', 'scene display', 'display', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (2, 'lesson_title_card', 'lesson title card', 'display', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (3, 'meter_compare', 'meter compare', 'meter', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (4, 'beat_feedback', 'beat feedback', 'meter', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (5, 'rhythm_drag_game', 'rhythm drag game', 'rhythm', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (6, 'creation_panel', 'creation panel', 'creation', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_definitions` VALUES (7, 'summary_page', 'summary page', 'display', '{}', 'active', '2026-07-06 16:58:43', '2026-07-06 16:58:43');

-- ----------------------------
-- Table structure for component_instances
-- ----------------------------
DROP TABLE IF EXISTS `component_instances`;
CREATE TABLE `component_instances`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `activity_node_id` bigint(20) NOT NULL,
  `component_definition_id` bigint(20) NOT NULL,
  `instance_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0,
  `props_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of component_instances
-- ----------------------------
INSERT INTO `component_instances` VALUES (1, 1, 1, 'scene_display', 1, '{\"componentKey\":\"scene_display\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (2, 1, 2, 'lesson_title_card', 2, '{\"componentKey\":\"lesson_title_card\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (3, 2, 3, 'meter_compare', 1, '{\"componentKey\":\"meter_compare\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (4, 2, 4, 'beat_feedback', 2, '{\"componentKey\":\"beat_feedback\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (5, 3, 5, 'rhythm_drag_game', 1, '{\"componentKey\":\"rhythm_drag_game\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (6, 4, 6, 'creation_panel', 1, '{\"componentKey\":\"creation_panel\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (7, 5, 7, 'summary_page', 1, '{\"componentKey\":\"summary_page\"}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `component_instances` VALUES (8, 6, 1, 'scene_display', 1, '{\"componentKey\":\"scene_display\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `component_instances` VALUES (9, 6, 2, 'lesson_title_card', 2, '{\"componentKey\":\"lesson_title_card\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `component_instances` VALUES (10, 7, 3, 'meter_compare', 1, '{\"componentKey\":\"meter_compare\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `component_instances` VALUES (11, 7, 4, 'beat_feedback', 2, '{\"componentKey\":\"beat_feedback\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `component_instances` VALUES (12, 8, 5, 'rhythm_drag_game', 1, '{\"componentKey\":\"rhythm_drag_game\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `component_instances` VALUES (13, 9, 6, 'creation_panel', 1, '{\"componentKey\":\"creation_panel\",\"rhythmCardCount\":4,\"hintEnabled\":true,\"difficulty\":\"normal\"}', '2026-07-09 13:16:55', '2026-07-09 13:43:25');
INSERT INTO `component_instances` VALUES (14, 10, 7, 'summary_page', 1, '{\"componentKey\":\"summary_page\"}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');

-- ----------------------------
-- Table structure for generation_jobs
-- ----------------------------
DROP TABLE IF EXISTS `generation_jobs`;
CREATE TABLE `generation_jobs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lesson_plan_id` bigint(20) NOT NULL,
  `created_by` bigint(20) NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `progress` int(11) NOT NULL DEFAULT 0,
  `request_params` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `started_at` datetime(0) NULL DEFAULT NULL,
  `finished_at` datetime(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of generation_jobs
-- ----------------------------
INSERT INTO `generation_jobs` VALUES (1, 1, 1, 'success', 100, '{\"style\":\"standard\",\"durationMinutes\":40}', NULL, '2026-07-06 16:58:43', '2026-07-06 16:58:43', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `generation_jobs` VALUES (2, 1, 1, 'success', 100, '{\"style\":\"standard\",\"durationMinutes\":40}', NULL, '2026-07-09 13:16:55', '2026-07-09 13:16:55', '2026-07-09 13:16:55', '2026-07-09 13:16:55');

-- ----------------------------
-- Table structure for interactive_packages
-- ----------------------------
DROP TABLE IF EXISTS `interactive_packages`;
CREATE TABLE `interactive_packages`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `lesson_plan_id` bigint(20) NULL DEFAULT NULL,
  `generation_job_id` bigint(20) NULL DEFAULT NULL,
  `owner_id` bigint(20) NOT NULL,
  `title` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `current_version_id` bigint(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of interactive_packages
-- ----------------------------
INSERT INTO `interactive_packages` VALUES (1, 1, 1, 1, '初中音乐课教案互动包', '基于教案《初中音乐课教案》生成的标准五段式互动课堂包', 'confirmed', '2026-07-06 16:58:43', '2026-07-06 16:59:07', 1);
INSERT INTO `interactive_packages` VALUES (2, 1, 2, 1, '初中音乐课教案互动包', '基于教案《初中音乐课教案》生成的标准五段式互动课堂包', 'modified', '2026-07-09 13:16:55', '2026-07-09 13:43:25', 3);

-- ----------------------------
-- Table structure for learning_events
-- ----------------------------
DROP TABLE IF EXISTS `learning_events`;
CREATE TABLE `learning_events`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `session_id` bigint(20) NOT NULL,
  `student_id` bigint(20) NULL DEFAULT NULL,
  `activity_node_id` bigint(20) NULL DEFAULT NULL,
  `event_type` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `occurred_at` datetime(0) NOT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of learning_events
-- ----------------------------

-- ----------------------------
-- Table structure for lesson_plans
-- ----------------------------
DROP TABLE IF EXISTS `lesson_plans`;
CREATE TABLE `lesson_plans`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `teacher_id` bigint(20) NOT NULL,
  `title` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `raw_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `parsed_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `raw_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `parsed_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `parse_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of lesson_plans
-- ----------------------------
INSERT INTO `lesson_plans` VALUES (1, 1, '初中音乐课教案', 'lesson-plans/47894643-ae12-422c-9f75-b3fca2345b08.docx', NULL, NULL, 'uploaded', '2026-07-06 16:58:32', '2026-07-06 16:58:32', '初中音乐课教案\n一、课题\n《青春舞曲》\n二、课型\n唱歌综合课\n三、课时\n1课时，40分钟\n四、教学对象\n初中七年级学生\n五、教学目标\n1. 情感态度与价值观目标\n通过学习新疆民歌《青春舞曲》，感受新疆民歌热情、活泼、富有舞蹈性的音乐风格，激发学生对民族音乐文化的兴趣，增强民族文化认同感。\n2. 过程与方法目标\n通过聆听、模唱、节奏练习、合作演唱和简单律动等方式，引导学生体验歌曲的节奏特点和情绪表达，提高学生的音乐感受力与表现力。\n3. 知识与技能目标\n学生能够准确演唱《青春舞曲》的旋律，掌握歌曲中切分节奏和附点节奏的特点，并能用自然、明亮、富有弹性的声音表现歌曲欢快的情绪。\n六、教学重点\n能够用自然、流畅、富有活力的声音完整演唱歌曲《青春舞曲》，表现歌曲欢快、热烈的情绪。\n七、教学难点\n掌握歌曲中的切分节奏和附点节奏，唱准旋律中的节奏变化，并能结合新疆音乐风格进行表现。\n八、教学准备\n多媒体课件、钢琴或电子琴、歌曲音频、新疆舞蹈或风景图片、节奏卡片。\n九、教学过程\n一、导入新课\n教师播放一段具有新疆风格的音乐片段，并展示新疆风景、民族服饰和舞蹈图片。\n教师提问：\n“同学们，听到这段音乐后，你们有什么感受？它的节奏是舒缓的，还是欢快的？”\n学生自由回答。\n教师总结：\n“新疆音乐常常具有鲜明的节奏感，旋律热情活泼，富有舞蹈性。今天我们要学习的歌曲就是一首具有新疆风格的民歌——《青春舞曲》。”\n二、初听歌曲，整体感知\n教师播放《青春舞曲》完整音频。\n学生带着问题聆听：\n歌曲的速度是怎样的？\n歌曲表达了怎样的情绪？\n歌曲给你留下最深印象的地方是什么？\n学生回答后，教师总结：\n《青春舞曲》旋律轻快，节奏鲜明，情绪活泼热烈，表达了人们珍惜青春、热爱生活的情感。\n三、节奏训练，突破难点\n教师出示歌曲中的典型节奏型：\nX X X | X X X |\nX. X X | X X X |\nX X X X | X - |\n教师带领学生拍手练习。\n练习方式：\n教师示范拍击节奏。\n学生跟随教师模仿。\n学生分组练习。\n加入身体律动，如拍手、拍腿、跺脚等。\n教师重点讲解：\n“这首歌曲节奏比较轻快，演唱时不能拖，要唱得有弹性。尤其是附点节奏和切分节奏，要唱出跳跃感。”\n四、学唱歌曲\n1. 教师范唱\n教师完整范唱歌曲，要求学生轻声跟唱，感受歌曲旋律。\n2. 分句教唱\n教师用钢琴或电子琴带领学生逐句学唱。\n重点指导：\n“太阳下山明早依旧爬上来”一句要唱得流畅自然。\n“美丽小鸟飞去无踪影”一句要注意节奏的准确性。\n“我的青春小鸟一样不回来”一句要唱出珍惜青春的情感。\n3. 学生完整演唱\n学生跟随伴奏完整演唱歌曲。\n教师提醒学生：\n演唱时声音要自然明亮，节奏要轻快，不能喊唱，也不能唱得过于沉重。\n五、歌曲处理与表现\n教师引导学生思考：\n“这首歌曲虽然旋律欢快，但歌词中也表达了青春易逝的含义。我们在演唱时既要唱出欢快感，也要唱出珍惜青春的情感。”\n教师组织学生进行不同形式的演唱：\n全班齐唱。\n男女生分组演唱。\n小组接龙演唱。\n加入简单律动演唱。\n学生可根据歌曲节奏加入拍手、摆手或简单新疆舞动作，使歌曲表现更加生动。\n六、拓展延伸\n教师简单介绍《青春舞曲》的创作背景：\n《青春舞曲》由王洛宾根据新疆民歌整理创编，旋律优美、节奏欢快，是一首广为流传的民族风格歌曲。\n教师提问：\n“为什么歌词中说‘青春小鸟一样不回来’？这句话给你什么启发？”\n学生思考并回答。\n教师总结：\n“青春是美好的，也是短暂的。我们要珍惜现在的学习生活，用积极的态度面对成长。”\n七、课堂小结\n教师总结本节课内容：\n“今天我们学习了新疆风格歌曲《青春舞曲》，感受了新疆民歌热情、活泼的音乐特点，练习了歌曲中的节奏难点，并尝试用演唱和律动表现歌曲情绪。希望同学们能够在音乐中感受民族文化的魅力，也懂得珍惜青春时光。”\n八、作业布置\n课后熟练演唱《青春舞曲》。\n查找一首自己喜欢的新疆民歌，下节课与同学分享歌曲名称和听后感受。\n思考：音乐作品如何表达对青春和生活的热爱？\n十、板书设计\n《青春舞曲》\n\n一、音乐风格：新疆民歌风格\n二、歌曲情绪：欢快、活泼、热烈\n三、节奏特点：切分节奏、附点节奏\n四、演唱要求：自然明亮、轻快有弹性\n五、主题思想：珍惜青春，热爱生活\n十一、教学反思\n本节课通过聆听、节奏练习、分句学唱和律动表现等方式，引导学生感受《青春舞曲》的音乐风格。学生能够较好地掌握歌曲旋律和基本节奏，但在切分节奏和附点节奏的准确表现上仍需加强。后续教学中可增加节奏游戏和小组合作展示，提高学生参与度和音乐表现力。\n', '{\"courseName\":\"初中音乐课教案\",\"grade\":\"初中七年级学生\",\"objectives\":[\"情感态度与价值观目标\",\"通过学习新疆民歌《青春舞曲》，感受新疆民歌热情、活泼、富有舞蹈性的音乐风格，激发学生对民族音乐文化的兴趣，增强民族文化认同感。\",\"过程与方法目标\",\"通过聆听、模唱、节奏练习、合作演唱和简单律动等方式，引导学生体验歌曲的节奏特点和情绪表达，提高学生的音乐感受力与表现力。\",\"知识与技能目标\",\"学生能够准确演唱《青春舞曲》的旋律，掌握歌曲中切分节奏和附点节奏的特点，并能用自然、明亮、富有弹性的声音表现歌曲欢快的情绪。\"],\"keyPoints\":[\"能够用自然、流畅、富有活力的声音完整演唱歌曲《青春舞曲》，表现歌曲欢快、热烈的情绪。\"],\"process\":[\"导入新课\",\"教师播放一段具有新疆风格的音乐片段，并展示新疆风景、民族服饰和舞蹈图片。\",\"教师提问：\",\"“同学们，听到这段音乐后，你们有什么感受？它的节奏是舒缓的，还是欢快的？”\",\"学生自由回答。\",\"教师总结：\",\"“新疆音乐常常具有鲜明的节奏感，旋律热情活泼，富有舞蹈性。今天我们要学习的歌曲就是一首具有新疆风格的民歌——《青春舞曲》。”\",\"初听歌曲，整体感知\",\"教师播放《青春舞曲》完整音频。\",\"学生带着问题聆听：\",\"歌曲的速度是怎样的？\",\"歌曲表达了怎样的情绪？\",\"歌曲给你留下最深印象的地方是什么？\",\"学生回答后，教师总结：\",\"《青春舞曲》旋律轻快，节奏鲜明，情绪活泼热烈，表达了人们珍惜青春、热爱生活的情感。\",\"节奏训练，突破难点\",\"教师出示歌曲中的典型节奏型：\",\"X X X | X X X |\",\"X. X X | X X X |\",\"X X X X | X - |\",\"教师带领学生拍手练习。\",\"练习方式：\",\"教师示范拍击节奏。\",\"学生跟随教师模仿。\",\"学生分组练习。\",\"加入身体律动，如拍手、拍腿、跺脚等。\",\"教师重点讲解：\",\"“这首歌曲节奏比较轻快，演唱时不能拖，要唱得有弹性。尤其是附点节奏和切分节奏，要唱出跳跃感。”\",\"学唱歌曲\",\"教师范唱\",\"教师完整范唱歌曲，要求学生轻声跟唱，感受歌曲旋律。\",\"分句教唱\",\"教师用钢琴或电子琴带领学生逐句学唱。\",\"重点指导：\",\"“太阳下山明早依旧爬上来”一句要唱得流畅自然。\",\"“美丽小鸟飞去无踪影”一句要注意节奏的准确性。\",\"“我的青春小鸟一样不回来”一句要唱出珍惜青春的情感。\",\"学生完整演唱\",\"学生跟随伴奏完整演唱歌曲。\",\"教师提醒学生：\",\"演唱时声音要自然明亮，节奏要轻快，不能喊唱，也不能唱得过于沉重。\",\"歌曲处理与表现\",\"教师引导学生思考：\",\"“这首歌曲虽然旋律欢快，但歌词中也表达了青春易逝的含义。我们在演唱时既要唱出欢快感，也要唱出珍惜青春的情感。”\",\"教师组织学生进行不同形式的演唱：\",\"全班齐唱。\",\"男女生分组演唱。\",\"小组接龙演唱。\",\"加入简单律动演唱。\",\"学生可根据歌曲节奏加入拍手、摆手或简单新疆舞动作，使歌曲表现更加生动。\",\"拓展延伸\",\"教师简单介绍《青春舞曲》的创作背景：\",\"《青春舞曲》由王洛宾根据新疆民歌整理创编，旋律优美、节奏欢快，是一首广为流传的民族风格歌曲。\",\"教师提问：\",\"“为什么歌词中说‘青春小鸟一样不回来’？这句话给你什么启发？”\",\"学生思考并回答。\",\"教师总结：\",\"“青春是美好的，也是短暂的。我们要珍惜现在的学习生活，用积极的态度面对成长。”\"],\"musicElements\":[\"节奏\",\"旋律\"]}', 'success');

-- ----------------------------
-- Table structure for package_modify_records
-- ----------------------------
DROP TABLE IF EXISTS `package_modify_records`;
CREATE TABLE `package_modify_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `version_id` bigint(20) NULL DEFAULT NULL,
  `modified_by` bigint(20) NOT NULL,
  `modify_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `modify_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of package_modify_records
-- ----------------------------
INSERT INTO `package_modify_records` VALUES (1, 2, 3, 1, 'node_config', '{\"nodeId\":9,\"modifyType\":\"node_config\",\"config\":{\"title\":\"创编工作坊\",\"description\":\"\",\"difficulty\":\"normal\",\"rhythmCardCount\":4,\"hintEnabled\":true,\"hidden\":false,\"componentInstanceId\":null,\"componentParams\":{}}}', '2026-07-09 13:43:25', '2026-07-09 13:43:25');

-- ----------------------------
-- Table structure for package_publications
-- ----------------------------
DROP TABLE IF EXISTS `package_publications`;
CREATE TABLE `package_publications`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `version_id` bigint(20) NOT NULL,
  `published_by` bigint(20) NOT NULL,
  `publish_channel` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'published',
  `published_at` datetime(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `class_id` bigint(20) NULL DEFAULT NULL,
  `review_enabled` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_package_publications_class_id`(`class_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of package_publications
-- ----------------------------
INSERT INTO `package_publications` VALUES (1, 2, 2, 1, 'classroom', 'published', '2026-07-09 13:43:01', '2026-07-09 13:43:01', '2026-07-09 13:43:01', 1, 1);
INSERT INTO `package_publications` VALUES (2, 2, 2, 1, 'classroom', 'published', '2026-07-09 13:43:06', '2026-07-09 13:43:06', '2026-07-09 13:43:06', 1, 0);
INSERT INTO `package_publications` VALUES (3, 2, 3, 1, 'classroom', 'published', '2026-07-09 13:43:40', '2026-07-09 13:43:40', '2026-07-09 13:43:40', 1, 0);

-- ----------------------------
-- Table structure for package_version_diffs
-- ----------------------------
DROP TABLE IF EXISTS `package_version_diffs`;
CREATE TABLE `package_version_diffs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `from_version_id` bigint(20) NOT NULL,
  `to_version_id` bigint(20) NOT NULL,
  `diff_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of package_version_diffs
-- ----------------------------
INSERT INTO `package_version_diffs` VALUES (1, 2, 2, 3, '{\"modifyType\":\"node_config\",\"request\":{\"nodeId\":9,\"modifyType\":\"node_config\",\"config\":{\"title\":\"创编工作坊\",\"description\":\"\",\"difficulty\":\"normal\",\"rhythmCardCount\":4,\"hintEnabled\":true,\"hidden\":false,\"componentInstanceId\":null,\"componentParams\":{}}},\"before\":{\"nodes\":[{\"configJson\":\"{\\\"title\\\":\\\"课堂入口页\\\",\\\"nodeType\\\":\\\"entry\\\",\\\"sortOrder\\\":1,\\\"componentKeys\\\":[\\\"scene_display\\\",\\\"lesson_title_card\\\"]}\",\"components\":[{\"componentDefinitionId\":1,\"instanceName\":\"scene_display\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"scene_display\\\"}\",\"id\":8},{\"componentDefinitionId\":2,\"instanceName\":\"lesson_title_card\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"lesson_title_card\\\"}\",\"id\":9}],\"sortOrder\":1,\"id\":6,\"title\":\"课堂入口页\",\"nodeType\":\"entry\"},{\"configJson\":\"{\\\"title\\\":\\\"节拍体验工具\\\",\\\"nodeType\\\":\\\"meter_experience\\\",\\\"sortOrder\\\":2,\\\"componentKeys\\\":[\\\"meter_compare\\\",\\\"beat_feedback\\\"]}\",\"components\":[{\"componentDefinitionId\":3,\"instanceName\":\"meter_compare\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"meter_compare\\\"}\",\"id\":10},{\"componentDefinitionId\":4,\"instanceName\":\"beat_feedback\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"beat_feedback\\\"}\",\"id\":11}],\"sortOrder\":2,\"id\":7,\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\"},{\"configJson\":\"{\\\"title\\\":\\\"节奏拖拽游戏\\\",\\\"nodeType\\\":\\\"rhythm_game\\\",\\\"sortOrder\\\":3,\\\"componentKeys\\\":[\\\"rhythm_drag_game\\\"]}\",\"components\":[{\"componentDefinitionId\":5,\"instanceName\":\"rhythm_drag_game\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"rhythm_drag_game\\\"}\",\"id\":12}],\"sortOrder\":3,\"id\":8,\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\"},{\"configJson\":\"{\\\"title\\\":\\\"创编工作坊\\\",\\\"nodeType\\\":\\\"creation_workshop\\\",\\\"sortOrder\\\":4,\\\"componentKeys\\\":[\\\"creation_panel\\\"]}\",\"components\":[{\"componentDefinitionId\":6,\"instanceName\":\"creation_panel\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"creation_panel\\\"}\",\"id\":13}],\"sortOrder\":4,\"id\":9,\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\"},{\"configJson\":\"{\\\"title\\\":\\\"展示总结页\\\",\\\"nodeType\\\":\\\"summary\\\",\\\"sortOrder\\\":5,\\\"componentKeys\\\":[\\\"summary_page\\\"]}\",\"components\":[{\"componentDefinitionId\":7,\"instanceName\":\"summary_page\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"summary_page\\\"}\",\"id\":14}],\"sortOrder\":5,\"id\":10,\"title\":\"展示总结页\",\"nodeType\":\"summary\"}]},\"after\":{\"nodes\":[{\"configJson\":\"{\\\"title\\\":\\\"课堂入口页\\\",\\\"nodeType\\\":\\\"entry\\\",\\\"sortOrder\\\":1,\\\"componentKeys\\\":[\\\"scene_display\\\",\\\"lesson_title_card\\\"]}\",\"components\":[{\"componentDefinitionId\":1,\"instanceName\":\"scene_display\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"scene_display\\\"}\",\"id\":8},{\"componentDefinitionId\":2,\"instanceName\":\"lesson_title_card\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"lesson_title_card\\\"}\",\"id\":9}],\"sortOrder\":1,\"id\":6,\"title\":\"课堂入口页\",\"nodeType\":\"entry\"},{\"configJson\":\"{\\\"title\\\":\\\"节拍体验工具\\\",\\\"nodeType\\\":\\\"meter_experience\\\",\\\"sortOrder\\\":2,\\\"componentKeys\\\":[\\\"meter_compare\\\",\\\"beat_feedback\\\"]}\",\"components\":[{\"componentDefinitionId\":3,\"instanceName\":\"meter_compare\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"meter_compare\\\"}\",\"id\":10},{\"componentDefinitionId\":4,\"instanceName\":\"beat_feedback\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"beat_feedback\\\"}\",\"id\":11}],\"sortOrder\":2,\"id\":7,\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\"},{\"configJson\":\"{\\\"title\\\":\\\"节奏拖拽游戏\\\",\\\"nodeType\\\":\\\"rhythm_game\\\",\\\"sortOrder\\\":3,\\\"componentKeys\\\":[\\\"rhythm_drag_game\\\"]}\",\"components\":[{\"componentDefinitionId\":5,\"instanceName\":\"rhythm_drag_game\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"rhythm_drag_game\\\"}\",\"id\":12}],\"sortOrder\":3,\"id\":8,\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\"},{\"configJson\":\"{\\\"title\\\":\\\"创编工作坊\\\",\\\"nodeType\\\":\\\"creation_workshop\\\",\\\"sortOrder\\\":4,\\\"componentKeys\\\":[\\\"creation_panel\\\"],\\\"description\\\":\\\"\\\",\\\"difficulty\\\":\\\"normal\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"hidden\\\":false}\",\"components\":[{\"componentDefinitionId\":6,\"instanceName\":\"creation_panel\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"creation_panel\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"difficulty\\\":\\\"normal\\\"}\",\"id\":13}],\"sortOrder\":4,\"id\":9,\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\"},{\"configJson\":\"{\\\"title\\\":\\\"展示总结页\\\",\\\"nodeType\\\":\\\"summary\\\",\\\"sortOrder\\\":5,\\\"componentKeys\\\":[\\\"summary_page\\\"]}\",\"components\":[{\"componentDefinitionId\":7,\"instanceName\":\"summary_page\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"summary_page\\\"}\",\"id\":14}],\"sortOrder\":5,\"id\":10,\"title\":\"展示总结页\",\"nodeType\":\"summary\"}]},\"nodeId\":9}', '2026-07-09 13:43:25', '2026-07-09 13:43:25');

-- ----------------------------
-- Table structure for package_versions
-- ----------------------------
DROP TABLE IF EXISTS `package_versions`;
CREATE TABLE `package_versions`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `version_no` int(11) NOT NULL,
  `created_by` bigint(20) NOT NULL,
  `snapshot_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'generated',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of package_versions
-- ----------------------------
INSERT INTO `package_versions` VALUES (1, 1, 1, 1, '{\"chain\":{\"title\":\"初中音乐课教案互动课堂\",\"steps\":[{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]},{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]},{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]},{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"]},{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}]},\"nodes\":[{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]},{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]},{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]},{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"]},{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}]}', '初始生成版本', '2026-07-06 16:58:43', '2026-07-06 16:59:07', 'confirmed');
INSERT INTO `package_versions` VALUES (2, 2, 1, 1, '{\"chain\":{\"title\":\"初中音乐课教案互动课堂\",\"steps\":[{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]},{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]},{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]},{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"]},{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}]},\"nodes\":[{\"title\":\"课堂入口页\",\"nodeType\":\"entry\",\"sortOrder\":1,\"componentKeys\":[\"scene_display\",\"lesson_title_card\"]},{\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\",\"sortOrder\":2,\"componentKeys\":[\"meter_compare\",\"beat_feedback\"]},{\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\",\"sortOrder\":3,\"componentKeys\":[\"rhythm_drag_game\"]},{\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\",\"sortOrder\":4,\"componentKeys\":[\"creation_panel\"]},{\"title\":\"展示总结页\",\"nodeType\":\"summary\",\"sortOrder\":5,\"componentKeys\":[\"summary_page\"]}]}', '初始生成版本', '2026-07-09 13:16:55', '2026-07-09 13:17:02', 'confirmed');
INSERT INTO `package_versions` VALUES (3, 2, 2, 1, '{\"nodes\":[{\"configJson\":\"{\\\"title\\\":\\\"课堂入口页\\\",\\\"nodeType\\\":\\\"entry\\\",\\\"sortOrder\\\":1,\\\"componentKeys\\\":[\\\"scene_display\\\",\\\"lesson_title_card\\\"]}\",\"components\":[{\"componentDefinitionId\":1,\"instanceName\":\"scene_display\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"scene_display\\\"}\",\"id\":8},{\"componentDefinitionId\":2,\"instanceName\":\"lesson_title_card\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"lesson_title_card\\\"}\",\"id\":9}],\"sortOrder\":1,\"id\":6,\"title\":\"课堂入口页\",\"nodeType\":\"entry\"},{\"configJson\":\"{\\\"title\\\":\\\"节拍体验工具\\\",\\\"nodeType\\\":\\\"meter_experience\\\",\\\"sortOrder\\\":2,\\\"componentKeys\\\":[\\\"meter_compare\\\",\\\"beat_feedback\\\"]}\",\"components\":[{\"componentDefinitionId\":3,\"instanceName\":\"meter_compare\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"meter_compare\\\"}\",\"id\":10},{\"componentDefinitionId\":4,\"instanceName\":\"beat_feedback\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"beat_feedback\\\"}\",\"id\":11}],\"sortOrder\":2,\"id\":7,\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\"},{\"configJson\":\"{\\\"title\\\":\\\"节奏拖拽游戏\\\",\\\"nodeType\\\":\\\"rhythm_game\\\",\\\"sortOrder\\\":3,\\\"componentKeys\\\":[\\\"rhythm_drag_game\\\"]}\",\"components\":[{\"componentDefinitionId\":5,\"instanceName\":\"rhythm_drag_game\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"rhythm_drag_game\\\"}\",\"id\":12}],\"sortOrder\":3,\"id\":8,\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\"},{\"configJson\":\"{\\\"title\\\":\\\"创编工作坊\\\",\\\"nodeType\\\":\\\"creation_workshop\\\",\\\"sortOrder\\\":4,\\\"componentKeys\\\":[\\\"creation_panel\\\"],\\\"description\\\":\\\"\\\",\\\"difficulty\\\":\\\"normal\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"hidden\\\":false}\",\"components\":[{\"componentDefinitionId\":6,\"instanceName\":\"creation_panel\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"creation_panel\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"difficulty\\\":\\\"normal\\\"}\",\"id\":13}],\"sortOrder\":4,\"id\":9,\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\"},{\"configJson\":\"{\\\"title\\\":\\\"展示总结页\\\",\\\"nodeType\\\":\\\"summary\\\",\\\"sortOrder\\\":5,\\\"componentKeys\\\":[\\\"summary_page\\\"]}\",\"components\":[{\"componentDefinitionId\":7,\"instanceName\":\"summary_page\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"summary_page\\\"}\",\"id\":14}],\"sortOrder\":5,\"id\":10,\"title\":\"展示总结页\",\"nodeType\":\"summary\"}]}', '参数级修改：nodeId=9', '2026-07-09 13:43:25', '2026-07-09 13:43:25', 'modified');

-- ----------------------------
-- Table structure for proposal_cards
-- ----------------------------
DROP TABLE IF EXISTS `proposal_cards`;
CREATE TABLE `proposal_cards`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `generation_job_id` bigint(20) NULL DEFAULT NULL,
  `package_id` bigint(20) NULL DEFAULT NULL,
  `title` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `confirm_status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of proposal_cards
-- ----------------------------
INSERT INTO `proposal_cards` VALUES (1, 1, 1, '互动包生成建议', '生成方案：初中音乐课教案互动课堂\n活动结构：课堂入口页 → 节拍体验工具 → 节奏拖拽游戏 → 创编工作坊 → 展示总结页\n质量评分：95\n建议：教师可根据课堂时长调整节奏拖拽游戏和创编工作坊的练习次数。', 'generated', '2026-07-06 16:58:43', '2026-07-06 16:59:07', 'confirmed');
INSERT INTO `proposal_cards` VALUES (2, 2, 2, '互动包生成建议', '生成方案：初中音乐课教案互动课堂\n活动结构：课堂入口页 → 节拍体验工具 → 节奏拖拽游戏 → 创编工作坊 → 展示总结页\n质量评分：95\n建议：教师可根据课堂时长调整节奏拖拽游戏和创编工作坊的练习次数。', 'generated', '2026-07-09 13:16:55', '2026-07-09 13:17:02', 'confirmed');

-- ----------------------------
-- Table structure for quality_reports
-- ----------------------------
DROP TABLE IF EXISTS `quality_reports`;
CREATE TABLE `quality_reports`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_id` bigint(20) NOT NULL,
  `version_id` bigint(20) NULL DEFAULT NULL,
  `score` int(11) NULL DEFAULT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `report_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of quality_reports
-- ----------------------------
INSERT INTO `quality_reports` VALUES (1, 1, 1, 95, 'passed', '{\"score\":95,\"status\":\"passed\",\"messages\":[\"已生成标准五段式音乐互动课堂活动链\",\"组件实例已覆盖入口、节拍、节奏、创编与总结环节\"]}', '2026-07-06 16:58:43', '2026-07-06 16:58:43');
INSERT INTO `quality_reports` VALUES (2, 2, 2, 95, 'passed', '{\"score\":95,\"status\":\"passed\",\"messages\":[\"已生成标准五段式音乐互动课堂活动链\",\"组件实例已覆盖入口、节拍、节奏、创编与总结环节\"]}', '2026-07-09 13:16:55', '2026-07-09 13:16:55');
INSERT INTO `quality_reports` VALUES (3, 2, 3, 90, 'passed', '{\"score\":90,\"message\":\"参数级修改已通过基础检查\",\"nodeId\":9,\"snapshot\":{\"nodes\":[{\"configJson\":\"{\\\"title\\\":\\\"课堂入口页\\\",\\\"nodeType\\\":\\\"entry\\\",\\\"sortOrder\\\":1,\\\"componentKeys\\\":[\\\"scene_display\\\",\\\"lesson_title_card\\\"]}\",\"components\":[{\"componentDefinitionId\":1,\"instanceName\":\"scene_display\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"scene_display\\\"}\",\"id\":8},{\"componentDefinitionId\":2,\"instanceName\":\"lesson_title_card\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"lesson_title_card\\\"}\",\"id\":9}],\"sortOrder\":1,\"id\":6,\"title\":\"课堂入口页\",\"nodeType\":\"entry\"},{\"configJson\":\"{\\\"title\\\":\\\"节拍体验工具\\\",\\\"nodeType\\\":\\\"meter_experience\\\",\\\"sortOrder\\\":2,\\\"componentKeys\\\":[\\\"meter_compare\\\",\\\"beat_feedback\\\"]}\",\"components\":[{\"componentDefinitionId\":3,\"instanceName\":\"meter_compare\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"meter_compare\\\"}\",\"id\":10},{\"componentDefinitionId\":4,\"instanceName\":\"beat_feedback\",\"sortOrder\":2,\"propsJson\":\"{\\\"componentKey\\\":\\\"beat_feedback\\\"}\",\"id\":11}],\"sortOrder\":2,\"id\":7,\"title\":\"节拍体验工具\",\"nodeType\":\"meter_experience\"},{\"configJson\":\"{\\\"title\\\":\\\"节奏拖拽游戏\\\",\\\"nodeType\\\":\\\"rhythm_game\\\",\\\"sortOrder\\\":3,\\\"componentKeys\\\":[\\\"rhythm_drag_game\\\"]}\",\"components\":[{\"componentDefinitionId\":5,\"instanceName\":\"rhythm_drag_game\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"rhythm_drag_game\\\"}\",\"id\":12}],\"sortOrder\":3,\"id\":8,\"title\":\"节奏拖拽游戏\",\"nodeType\":\"rhythm_game\"},{\"configJson\":\"{\\\"title\\\":\\\"创编工作坊\\\",\\\"nodeType\\\":\\\"creation_workshop\\\",\\\"sortOrder\\\":4,\\\"componentKeys\\\":[\\\"creation_panel\\\"],\\\"description\\\":\\\"\\\",\\\"difficulty\\\":\\\"normal\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"hidden\\\":false}\",\"components\":[{\"componentDefinitionId\":6,\"instanceName\":\"creation_panel\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"creation_panel\\\",\\\"rhythmCardCount\\\":4,\\\"hintEnabled\\\":true,\\\"difficulty\\\":\\\"normal\\\"}\",\"id\":13}],\"sortOrder\":4,\"id\":9,\"title\":\"创编工作坊\",\"nodeType\":\"creation_workshop\"},{\"configJson\":\"{\\\"title\\\":\\\"展示总结页\\\",\\\"nodeType\\\":\\\"summary\\\",\\\"sortOrder\\\":5,\\\"componentKeys\\\":[\\\"summary_page\\\"]}\",\"components\":[{\"componentDefinitionId\":7,\"instanceName\":\"summary_page\",\"sortOrder\":1,\"propsJson\":\"{\\\"componentKey\\\":\\\"summary_page\\\"}\",\"id\":14}],\"sortOrder\":5,\"id\":10,\"title\":\"展示总结页\",\"nodeType\":\"summary\"}]},\"status\":\"passed\"}', '2026-07-09 13:43:25', '2026-07-09 13:43:25');

-- ----------------------------
-- Table structure for session_node_states
-- ----------------------------
DROP TABLE IF EXISTS `session_node_states`;
CREATE TABLE `session_node_states`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `session_id` bigint(20) NOT NULL,
  `activity_node_id` bigint(20) NOT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'locked',
  `state_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `unlocked_at` datetime(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of session_node_states
-- ----------------------------

-- ----------------------------
-- Table structure for student_progress
-- ----------------------------
DROP TABLE IF EXISTS `student_progress`;
CREATE TABLE `student_progress`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `session_id` bigint(20) NOT NULL,
  `student_id` bigint(20) NOT NULL,
  `current_node_id` bigint(20) NULL DEFAULT NULL,
  `progress` int(11) NOT NULL DEFAULT 0,
  `score` int(11) NULL DEFAULT NULL,
  `last_active_at` datetime(0) NULL DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  `progress_status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'not_started',
  `wrong_count` int(11) NOT NULL DEFAULT 0,
  `hint_used_count` int(11) NOT NULL DEFAULT 0,
  `duration_seconds` int(11) NOT NULL DEFAULT 0,
  `result_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of student_progress
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `real_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_users_username`(`username`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'teacher001', '$2a$10$1BhC7mVV4TnE4J3tpyFuz.OAwvfIIkv/bTtObuZiZEAZQHQxcWnvK', '教师001', 'teacher', NULL, NULL, 'active', '2026-06-27 16:43:02', '2026-06-27 16:43:02');
INSERT INTO `users` VALUES (2, 'student001', '$2a$10$1BhC7mVV4TnE4J3tpyFuz.OAwvfIIkv/bTtObuZiZEAZQHQxcWnvK', '学生001', 'student', NULL, NULL, 'active', '2026-06-27 16:48:16', '2026-06-27 16:48:16');

SET FOREIGN_KEY_CHECKS = 1;
