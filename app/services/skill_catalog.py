from __future__ import annotations


APP_SKILLS = [
    {
        "id": "listening_basic_pitch",
        "name": "体验性活动生成",
        "layer": "listening",
        "template": "Blueprint_Listen",
        "template_role": "activity_blueprint",
        "description": "上传音频后，直接切换调式、调性、节奏、速度和音色，生成可试听的课堂版本。",
        "endpoint": "/api/listening/process",
    },
    {
        "id": "performance_game",
        "name": "表现性闯关生成",
        "layer": "performance",
        "template": "Blueprint_Performance",
        "template_role": "activity_blueprint",
        "description": "根据歌曲、学段、目标和关卡数量，拆分成阶梯式课堂闯关活动。",
        "endpoint": "/api/performance/generate",
    },
    {
        "id": "performance_template_library",
        "name": "表现性游戏模板库",
        "layer": "performance",
        "template": "Blueprint_Performance",
        "template_role": "activity_blueprint_library",
        "description": "按教学重点选择合适表现母版，例如节奏、打击乐、力度渐强适配沉浸式音乐闯关。",
        "endpoint": "/api/assets/performance-templates",
    },
    {
        "id": "creation_puzzle",
        "name": "创造性音乐拼图",
        "layer": "creation",
        "template": "Blueprint_Creation",
        "template_role": "activity_blueprint",
        "description": "根据主音、调式、节奏、情绪和结构功能生成可拖拽拼图块，学生拼成一首曲子。",
        "endpoint": "/api/creation/generate",
    },
    {
        "id": "music_game_builder",
        "name": "音乐小游戏生成",
        "layer": "music_game",
        "template": "Blueprint_MusicGame",
        "template_role": "activity_blueprint",
        "description": "根据音乐概念和玩法要求生成可操作小游戏，例如节奏赛跑、音高飞行、翻牌匹配或角色拖拽。",
        "endpoint": "/api/agent/generate-webpage",
    },
    {
        "id": "webpage_composer",
        "name": "一键网页生成",
        "layer": "agent",
        "description": "把用户自然语言需求转成卡通可爱、交互性强的课堂网页工具。",
        "endpoint": "/api/agent/generate-webpage",
    },
    {
        "id": "music_education_knowledge",
        "name": "音乐教育知识库",
        "layer": "pedagogy",
        "description": "提供课程标准锚点、年级能力分层、曲目教学重点和音乐课堂评价建议。",
        "endpoint": "/api/agent/skills",
    },
    {
        "id": "ai_image_generation",
        "name": "课堂真实图片生成",
        "layer": "visual",
        "description": "根据课例重点和音乐游戏机制生成背景图、组件图；不可用时自动回退到本地预设素材。",
        "endpoint": "/api/assets/image-generation/status",
    },
]


def list_app_skills() -> list[dict]:
    return APP_SKILLS
