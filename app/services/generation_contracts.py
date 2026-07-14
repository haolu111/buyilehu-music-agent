from __future__ import annotations

from typing import Any

from app.services.music_game_library import canonical_game_type, detect_template_match_from_text
from app.services.template_library import technical_strategy_for_activity, template_id_for_activity
from app.services.template_library import MUSIC_TEMPLATES
from app.services.visual_asset_library import select_visual_asset_pack


ALLOWED_ACTIVITY_TYPES = {"listening", "performance", "creation", "music_game", "mixed"}
GENERIC_TEMPLATE_IDS = {
    str(template.get("id", "")).strip()
    for template in MUSIC_TEMPLATES.values()
    if str(template.get("id", "")).strip()
} | {
    str(template.get("legacy_id", "")).strip()
    for template in MUSIC_TEMPLATES.values()
    if str(template.get("legacy_id", "")).strip()
}

ALLOWED_TECH_ROUTE = {
    "agent_runtime": "OpenCode Server / CLI / SDK",
    "backend_api": "FastAPI",
    "audio_to_midi": "Basic Pitch",
    "music_theory": "music21-compatible theory layer; current MVP uses pretty_midi/mido primitives",
    "midi_editing": "pretty_midi + mido",
    "audio_preview": "Browser playback must use sampled SoundFont first from local server assets: /runtime-assets/soundfont-player/soundfont-player.js and /runtime-assets/midi-js-soundfonts/FluidR3_GM/. External CDN/GitHub is fallback only; oscillator synthesis is emergency fallback only",
    "frontend": "Generated HTML/CSS/JavaScript artifact pages",
    "interaction": "SVG / Canvas / drag-and-drop / sampled SoundFont playback / Web Audio fallback",
}

SAMPLED_AUDIO_REQUIREMENTS = [
    "所有生成网页里的乐器音色必须优先使用真实采样 SoundFont，不允许只用 oscillator/sine/sawtooth/triangle 电子合成音作为主要音色。",
    "优先引入本地 /runtime-assets/soundfont-player/soundfont-player.js，备用 /static/assets/soundfont-player/soundfont-player.js；通过 Soundfont.instrument(audioContext, instrumentName, { soundfont: 'FluidR3_GM', format: 'mp3', nameToUrl }) 播放，nameToUrl 必须先指向 /runtime-assets/midi-js-soundfonts/。",
    "常用映射：钢琴 acoustic_grand_piano，小提琴 violin，长笛 flute，古筝/筝类 koto，吉他 acoustic_guitar_nylon，大提琴 cello，单簧管 clarinet，木琴 xylophone。",
    "只有在 SoundFont 资源加载失败时，才允许使用 Web Audio oscillator 作为降级提示音，并且页面摘要需说明已内置采样音色优先策略。",
]

STUDENT_PAGE_CONTRACT = [
    "学生可见文字必须少：标题短、任务一句话、规则用 3 个以内短标签；不要堆长段落、教学设计原因或质量检查清单。",
    "首屏必须是可操作的大模块：主按钮、卡片、拖拽区、画布或跑道要占页面主体；触控按钮高度至少 56px，主要卡片/操作区不能小碎。",
    "不要浪费空间：减少空白装饰和大段说明，每屏至少出现一个可点击、可拖拽、可播放或可反馈的区域。",
    "页面给学生用，风格要有闯关感、角色感、徽章/进度/即时反馈，但趣味必须服务音乐任务。",
]

AGENT_ROLES = [
    {
        "id": "music-requirement-planner",
        "responsibility": "把教师自然语言需求拆成聆听、表现、创造三类产物规格。",
    },
    {
        "id": "python-music-coder",
        "responsibility": "在限定音乐技术路线内生成或修改 Python MIDI 分析与处理插件。",
    },
    {
        "id": "lesson-game-designer",
        "responsibility": "生成表现性闯关关卡、教师说明、学生任务和评价规则。",
    },
    {
        "id": "creative-tool-builder",
        "responsibility": "生成音乐拼图、旋律网格和课堂创作交互组件。",
    },
    {
        "id": "frontend-artifact-builder",
        "responsibility": "把规格渲染为可预览、可导出的网页产物，而不是改变智能体主界面。",
    },
]

PYTHON_PLUGIN_CONTRACT = {
    "interface": "MidiTransform",
    "required_methods": ["analyze(midi_path) -> dict", "transform(midi_path, output_path, params) -> dict"],
    "required_result_fields": [
        "analysis",
        "changed_elements",
        "music_reasoning",
        "output_midi",
        "preview_audio",
    ],
    "guardrails": [
        "只读写任务工作区内文件",
        "不发起网络请求",
        "保留原始 MIDI，所有修改写入新版本",
        "输出前检查 MIDI 非空、音高范围 0-127、时值为正",
    ],
}


def _resolve_music_game_template_id(spec: dict[str, Any]) -> str:
    game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    prompt_contract = spec.get("user_prompt_contract", {}) if isinstance(spec.get("user_prompt_contract"), dict) else {}
    original_need = str(prompt_contract.get("original_user_need") or spec.get("original_user_need") or "")
    candidates = [
        spec.get("matched_template_id"),
        game.get("matched_template_id"),
        spec.get("template_id"),
    ]
    for candidate in candidates:
        raw = str(candidate or "").strip()
        if not raw or raw in GENERIC_TEMPLATE_IDS:
            continue
        canonical = canonical_game_type(raw)
        if canonical and canonical != "lesson_mission_game":
            return canonical
    explicit_match = detect_template_match_from_text(original_need)
    if explicit_match:
        canonical = canonical_game_type(explicit_match)
        if canonical and canonical != "lesson_mission_game":
            return canonical
    return ""


def apply_generation_mode(spec: dict[str, Any], activity_type: str) -> dict[str, Any]:
    enriched = dict(spec)
    strategy = dict(technical_strategy_for_activity(activity_type))

    if activity_type != "music_game":
        template_id = str(enriched.get("template_id") or template_id_for_activity(activity_type)).strip()
        enriched["template_id"] = template_id
        enriched["blueprint_id"] = template_id
        enriched["template_role"] = "activity_blueprint"
        enriched["artifact_generation_mode"] = "template"
        enriched["template_policy"] = "activity_blueprint"
        enriched["matched_template_id"] = template_id
        enriched["technical_strategy"] = strategy
        return enriched

    matched_template_id = _resolve_music_game_template_id(enriched)
    blueprint_plan = dict(enriched.get("blueprint_plan", {}))
    generation_strategy = dict(enriched.get("generation_strategy", {}))

    if matched_template_id:
        enriched["template_id"] = matched_template_id
        enriched["blueprint_id"] = matched_template_id
        enriched["template_role"] = "matched_game_template"
        enriched["artifact_generation_mode"] = "template"
        enriched["template_policy"] = "prefer_matched_template"
        enriched["matched_template_id"] = matched_template_id
        blueprint_plan.setdefault("selection_reason", "当前玩法命中了现成音乐游戏模板，可直接在模板骨架上深化内容。")
        generation_strategy["mode"] = "matched_template_music_game"
        generation_strategy["template_policy"] = "prefer_matched_template"
        strategy.update(
            {
                "template": matched_template_id,
                "blueprint_id": matched_template_id,
                "blueprint_label": blueprint_plan.get("blueprint_label", "已匹配音乐游戏模板"),
            }
        )
    else:
        enriched["template_id"] = ""
        enriched["blueprint_id"] = "OpenEnded_MusicGame"
        enriched["template_role"] = "open_generation"
        enriched["artifact_generation_mode"] = "freeform"
        enriched["template_policy"] = "allow_free_generation"
        enriched["matched_template_id"] = ""
        blueprint_plan["blueprint_id"] = "OpenEnded_MusicGame"
        blueprint_plan["blueprint_label"] = "自由生成音乐游戏"
        blueprint_plan["selection_reason"] = "当前玩法没有命中现成模板，必须围绕教案目标、歌曲材料和 music_logic_contract 自由生成。"
        blueprint_plan.setdefault(
            "primary_interaction",
            enriched.get("interaction_model", {}).get("primary")
            or enriched.get("music_game", {}).get("game_type")
            or "custom_music_game",
        )
        generation_strategy["mode"] = "freeform_music_game"
        generation_strategy["template_policy"] = "no_forced_template"
        generation_strategy["artifact_goal"] = "生成围绕当前课例和音乐数据的真实可玩音乐游戏网页，而不是套用现成模板。"
        strategy.update(
            {
                "template": "",
                "blueprint_id": "OpenEnded_MusicGame",
                "blueprint_label": "自由生成音乐游戏",
                "rules": list(strategy.get("rules", []))
                + ["没有命中现成模板时，必须围绕歌曲材料、课堂目标和 music_logic_contract 自由生成页面，不能硬套任何内置模板。"],
            }
        )

    enriched["blueprint_plan"] = blueprint_plan
    enriched["generation_strategy"] = generation_strategy
    enriched["technical_strategy"] = strategy
    return enriched


def lock_spec_to_activity_type(spec: dict[str, Any], activity_type: str, model_gateway: Any) -> dict[str, Any]:
    """Make the user's selected generation target the final source of truth."""

    enriched = dict(spec)
    if activity_type not in ALLOWED_ACTIVITY_TYPES:
        activity_type = "mixed"
    enriched["activity_type"] = activity_type
    lesson_game_contract = enriched.get("lesson_game_contract") if isinstance(enriched.get("lesson_game_contract"), dict) else {}
    if activity_type == "music_game" and lesson_game_contract:
        music_game = enriched.get("music_game", {}) if isinstance(enriched.get("music_game"), dict) else {}
        playable_game = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
        enriched["artifact_generation_mode"] = "prefer_scaffold"
        enriched["template_id"] = "lesson_game_contract_playable_scaffold"
        enriched["blueprint_plan"] = {
            "blueprint_id": "Reusable_Playable_Scaffold",
            "blueprint_label": "可复用玩法骨架",
            "selection_reason": "教案小游戏先尝试复用稳定玩法运行时；未命中时再进入自由生成。",
            "primary_interaction": playable_game.get("operation_type") or "lesson_mission_game",
        }
        enriched["generation_strategy"] = {
            "mode": "prefer_playable_scaffold_then_freeform",
            "artifact_goal": "先锁定教案任务和成熟玩法底盘；命中成熟模板时由 React 学生运行时组装，未命中骨架时再进入自由生成。",
            "opencode_execution_target": "命中成熟模板时只允许产出 React 可消费的表现层包；未命中骨架时做受教案契约约束的自由生成；失败时只修复当前 OpenCode 产物。",
            "prefer_incremental_revision": True,
            "scaffold_policy": "prefer_playable_scaffold",
            "freeform_fallback": True,
            "render_priority": [
                "lesson_game_contract",
                "music_logic_contract",
                "playable_game",
                "real_sound_playback",
                "student_game_loop",
            ],
        }
        enriched["selected_skills"] = model_gateway._skills_for_activity(activity_type)
        enriched["listening"] = {
            **dict(enriched.get("listening", {})),
            "enabled": False,
        }
        enriched["performance"] = {
            **dict(enriched.get("performance", {})),
            "enabled": False,
        }
        enriched["creation"] = {
            **dict(enriched.get("creation", {})),
            "enabled": False,
        }
        enriched["music_game"] = {
            **dict(enriched.get("music_game", {})),
            "enabled": True,
        }
        return enriched
    lock_need_text = " ".join(
        [
            str(enriched.get("title", "")),
            str(enriched.get("subtitle", "")),
            str(enriched.get("song_name", "")),
            str(enriched.get("target_music_element", "")),
        ]
    ).strip()
    enriched["blueprint_plan"] = model_gateway._blueprint_plan_for_need(lock_need_text, activity_type)
    enriched["generation_strategy"] = model_gateway._generation_strategy_for_need(lock_need_text, activity_type)
    enriched["selected_skills"] = model_gateway._skills_for_activity(activity_type)
    enriched = apply_generation_mode(enriched, activity_type)

    enriched["listening"] = {
        **dict(enriched.get("listening", {})),
        "enabled": activity_type in {"listening", "mixed"},
    }
    enriched["performance"] = {
        **dict(enriched.get("performance", {})),
        "enabled": activity_type in {"performance", "mixed"},
    }
    enriched["creation"] = {
        **dict(enriched.get("creation", {})),
        "enabled": activity_type in {"creation", "mixed"},
    }
    enriched["music_game"] = {
        **dict(enriched.get("music_game", {})),
        "enabled": activity_type == "music_game",
    }
    active_modules = [
        module
        for module in ["listening", "performance", "creation", "music_game"]
        if isinstance(enriched.get(module), dict) and enriched[module].get("enabled")
    ]
    enriched["activity_type_lock"] = {
        "enabled": True,
        "activity_type": activity_type,
        "active_modules": active_modules,
        "reason": "用户在生成目标中明确选择，课例上下文和自检只能补充内容，不能改写产物类型。",
    }
    return enriched


def attach_visual_asset_pack(spec: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(spec)
    pack = select_visual_asset_pack(enriched)
    enriched["visual_asset_pack"] = pack
    if isinstance(enriched.get("music_game"), dict):
        enriched["music_game"] = {**enriched["music_game"], "visual_asset_pack": pack}
    visual_theme = dict(enriched.get("visual_theme", {}))
    visual_theme["asset_pack_id"] = pack["id"]
    visual_theme["illustration_style"] = f"{visual_theme.get('illustration_style', '课堂插图')}；使用预设素材包“{pack['label']}”"
    enriched["visual_theme"] = visual_theme
    return enriched
