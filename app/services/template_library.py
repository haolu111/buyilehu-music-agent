from __future__ import annotations


MUSIC_TEMPLATES = {
    "listening": {
        "id": "Blueprint_Listen",
        "legacy_id": "Template_Listen",
        "label": "聆听母版",
        "snippet": "audio_to_midi + element_transform + comparison_player",
        "rules": [
            "静默调用音频转 MIDI 与要素变换流水线",
            "前端只呈现上传、要素按钮、试听与课堂提示",
            "只在聆听体验维度启用音频分析",
        ],
    },
    "performance": {
        "id": "Blueprint_Performance",
        "legacy_id": "Template_Performance",
        "label": "表现母版",
        "snippet": "LevelController + stage_state + classroom_feedback",
        "rules": [
            "使用关卡控制器管理解锁、完成状态和课堂反馈",
            "根据 JSON 关卡数据动态生成闯关 UI",
            "不触发音频上传、MIDI 分析或音乐改写流程",
        ],
    },
    "creation": {
        "id": "Blueprint_Creation",
        "legacy_id": "Template_Creation",
        "label": "创造母版",
        "snippet": "AssetLoader + drag_drop_board + creation_rules",
        "rules": [
            "使用交互资产加载器呈现拖拽、填空、续写或重组素材",
            "根据创作方式加载不同的交互逻辑",
            "不触发音频上传、MIDI 分析或音乐改写流程",
        ],
    },
    "music_game": {
        "id": "Blueprint_MusicGame",
        "legacy_id": "Template_MusicGame",
        "label": "音乐小游戏母版",
        "snippet": "music_rule_mapper + game_mechanics + playful_feedback",
        "rules": [
            "把教师输入的音乐概念映射成游戏规则、角色、动作和反馈",
            "根据玩法动态生成拖拽、点击、匹配、赛跑或闯关交互",
            "必须包含可操作目标、即时反馈、重新挑战和课堂讨论提示",
        ],
    },
    "mixed": {
        "id": "Blueprint_Mixed",
        "legacy_id": "Template_Mixed",
        "label": "综合母版",
        "snippet": "Blueprint_Listen + Blueprint_Performance + Blueprint_Creation",
        "rules": [
            "按维度分别挂载聆听引擎、关卡控制器和创作资产加载器",
            "只有聆听维度会触发音频分析流程",
        ],
    },
}


def template_id_for_activity(activity_type: str) -> str:
    return MUSIC_TEMPLATES.get(activity_type, MUSIC_TEMPLATES["mixed"])["id"]


def technical_strategy_for_activity(activity_type: str) -> dict:
    template = MUSIC_TEMPLATES.get(activity_type, MUSIC_TEMPLATES["mixed"])
    return {
        "template": template["id"],
        "blueprint_id": template["id"],
        "legacy_template_id": template.get("legacy_id", template["id"]),
        "blueprint_label": template.get("label", template["id"]),
        "snippet": template["snippet"],
        "rules": template["rules"],
    }
