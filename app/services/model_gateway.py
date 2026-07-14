from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any
import httpx

from app.services.activity_guidance import build_guidance, infer_activity_type
from app.services.component_library import (
    component_prompt_catalog,
    components_for_interaction,
    normalize_component_ids,
)
from app.services.generation_contracts import apply_generation_mode
from app.services.game_template_registry import list_game_templates
from app.services.lesson_designer import generate_agent_plan, generate_creation_puzzle, generate_game_plan
from app.services.lesson_designer import GameRequest, PuzzleRequest
from app.services.llm_config import llm_runtime_config
from app.services.music_game_library import (
    build_music_game_blueprint,
    canonical_game_type,
    detect_template_match_from_text,
    game_form_for_type,
    infer_game_type_from_text,
)
from app.services.music_logic_contract import attach_music_logic_contract, build_music_logic_contract
from app.services.music_education_knowledge import compact_prompt_context
from app.services.template_library import technical_strategy_for_activity, template_id_for_activity


INSPIRATION_TEMPLATE_LABELS = {
    "beat_guardian_core": "节拍守卫",
    "pitch_ladder_core": "音高爬梯",
    "rhythm_echo_core": "节奏复刻",
    "solfege_target_core": "唱名打靶",
    "timbre_detective_core": "音色侦探",
    "form_treasure_core": "曲式寻宝",
    "composition_puzzle_core": "拼图创编工坊",
}

INSPIRATION_TEMPLATE_REASONS = {
    "beat_guardian_core": "它覆盖稳定拍、强拍、弱拍、拍号感和进入时机，适合把学生操作收束到听拍、预判和同步反馈。",
    "pitch_ladder_core": "它覆盖音高高低、旋律走向、上行下行和级进跳进，适合把旋律听辨变成可操作的音高路线。",
    "rhythm_echo_core": "它覆盖听示范、拍回节奏、节奏记忆和接龙复现，适合把节奏型训练做成即时反馈挑战。",
    "solfege_target_core": "它覆盖唱名听辨、击中目标和唱回确认，适合把内听与模唱落实到明确的学生动作。",
    "timbre_detective_core": "它覆盖乐器音色、声音证据和音色词表达，适合把听辨判断变成找证据的推理任务。",
    "form_treasure_core": "它覆盖段落结构、重复对比、ABA 和再现，适合把曲式听辨变成排路线和说依据。",
    "composition_puzzle_core": "它覆盖节奏/旋律素材拼接、试听验证和创编说明，适合把创作规则变成可拖拽的作品轨道。",
}

INSPIRATION_TEMPLATE_NEED_HINTS = {
    "beat_guardian_core": "请生成一个节拍守卫类音乐游戏，围绕强拍、弱拍、拍号感或进入时机设计听拍、预判、同步点击和即时反馈。",
    "pitch_ladder_core": "请生成一个音高爬梯类音乐游戏，围绕音高高低、旋律走向或上行下行设计听辨、定位、模唱和反馈。",
    "rhythm_echo_core": "请生成一个节奏复刻类音乐游戏，围绕节奏型听辨、拍回和接龙设计示范播放、学生复现、即时评分和重试。",
    "solfege_target_core": "请生成一个唱名打靶类音乐游戏，围绕唱名听辨和唱回确认设计听目标音、击中唱名、开口唱回和反馈。",
    "timbre_detective_core": "请生成一个音色侦探类音乐游戏，围绕乐器音色听辨设计听声音证物、选择对象、贴音色证据和说明理由。",
    "form_treasure_core": "请生成一个曲式寻宝类音乐游戏，围绕段落结构或 ABA 设计听段落、排列结构卡、验证路线和说出依据。",
    "composition_puzzle_core": "请生成一个拼图创编工坊类音乐游戏，围绕节奏或旋律素材创编设计拖拽拼接、试听、规则检查和修改展示。",
}

INSPIRATION_UNSUPPORTED_TEMPLATE_KEYWORDS = (
    "力度",
    "声音强弱",
    "强弱变化",
    "渐强",
    "渐弱",
    "速度",
    "渐快",
    "渐慢",
    "快慢",
    "情绪变化",
    "表情变化",
)


SYSTEM_PROMPT = """
你是不亦乐乎-音乐游戏生成智能体的后台规格生成器，一个由 OpenCode 驱动的中小学音乐课堂游戏生成智能体。
你的任务是把教师的自然语言需求，转换成一个独立可运行音乐工具产物的 JSON 规格。

必须遵守：
1. activity_type 只能是 listening、performance、creation、music_game、mixed。
2. 生成结果是独立产物页面，不是智能体主界面；智能体主界面只负责接收需求、展示进度和产物卡片。
3. listening 代表聆听体验产物：使用聆听母版 Blueprint_Listen 作为生成底座，网页必须让用户上传音频，并直接选择调式、调性、节奏、速度、音色等要素；所有音乐要素默认必须保持原样，只有用户明确选择某个要素变化时才改变那个要素；不要向用户展示底层技术名词。
4. performance 代表表现训练产物：使用表现母版 Blueprint_Performance 作为生成底座，只根据歌曲、节奏型、学段、目标和用户要求拆分关卡，形成阶梯式闯关任务；绝不要求音频上传或 MIDI 分析。
5. creation 代表创意活动产物：使用创造母版 Blueprint_Creation 作为生成底座，根据创作方式生成拖拽拼图、填空、续写、风格重组或网格旋律线组件；绝不要求音频上传或 MIDI 分析。
6. music_game 代表音乐小游戏产物：使用音乐小游戏母版 Blueprint_MusicGame 作为生成底座，把用户给出的音乐概念、角色、规则和玩法生成可操作小游戏；不能只输出文字说明。
7. mixed 可以组合以上多种活动。
8. 输出必须适合课堂直接使用，语言简洁、具体、有教学价值。
9. 生成的网页必须交互性强，按钮文案要像课堂伙伴而不是技术工具。
10. 如果用户指定关卡、创作规则或游戏规则，必须优先保留用户原始内容。
11. 如果生成网格线作曲工具，必须遵守：横轴每格代表 1 个十六分音符；纵轴每格代表 1 个半音；左侧 y 轴显示首调唱名；用户可以选择调性。
12. 如果生成创造类工具，必须支持多种音色试听；网格线作曲工具必须支持双声部，用户可以指定当前绘制声部，并分别为两个声部选择音色。
13. 创造类工具播放时要尽量连贯：旋律线需要补齐中间格点、合并连续同音，并提供自动、自然、连奏、断奏、拨弦等演奏方式。
14. 必须输出 interaction_model、scoring、runtime_behaviors、visual_theme 四个交互方案字段，用来指导 OpenCode 生成真实互动页面。
15. interaction_model 要说明主要玩法、组件、学生动作、教师控制和产出；scoring 要说明评价维度和反馈方式；runtime_behaviors 要说明倒计时、自动播放、进度保存、解锁、重置等运行行为；visual_theme 要说明视觉主题、版式、配色、插图和动效方向。
""".strip()


POLISH_SYSTEM_PROMPT = """
你是音乐教师的课堂活动需求润色助手。
请把用户的零散想法改写成一段清晰、具体、可用于生成音乐课堂工具的中文需求。

要求：
1. 不解释过程，只输出润色后的需求文本。
2. 保留用户提到的曲目、学段、活动形式、关卡、调式、节奏、音色、创作规则等信息。
3. 如果用户信息不足，可以温和补足常见课堂要素，但不要编造具体曲目。
4. 不出现技术路线、代码、模型、后台、接口等技术词。
5. 文本控制在 80 到 180 个中文字符之间。
""".strip()


TOOL_SPEC_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "activity_type": {"type": "string", "enum": ["listening", "performance", "creation", "music_game", "mixed"]},
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "grade_band": {"type": "string"},
        "song_name": {"type": "string"},
        "selected_skills": {"type": "array", "items": {"type": "string"}},
        "listening": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enabled": {"type": "boolean"},
                "tonic": {"type": "string"},
                "mode": {"type": "string"},
                "tempo_multiplier": {"type": "number"},
                "rhythm_density": {"type": "string"},
                "instrument": {"type": "string"},
                "task": {"type": "string"},
            },
            "required": ["enabled", "tonic", "mode", "tempo_multiplier", "rhythm_density", "instrument", "task"],
        },
        "performance": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enabled": {"type": "boolean"},
                "theme": {"type": "string"},
                "target_skill": {"type": "string"},
                "stage_count": {"type": "integer"},
                "levels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "title": {"type": "string"},
                            "goal": {"type": "string"},
                            "student_task": {"type": "string"},
                            "success_rule": {"type": "string"},
                        },
                        "required": ["title", "goal", "student_task", "success_rule"],
                    },
                },
            },
            "required": ["enabled", "theme", "target_skill", "stage_count", "levels"],
        },
        "creation": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enabled": {"type": "boolean"},
                "tonic": {"type": "string"},
                "mode": {"type": "string"},
                "bars": {"type": "integer"},
                "mood": {"type": "string"},
                "pieces": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string"},
                            "pitch": {"type": "string"},
                            "rhythm": {"type": "string"},
                            "function": {"type": "string"},
                        },
                        "required": ["id", "pitch", "rhythm", "function"],
                    },
                },
            },
            "required": ["enabled", "tonic", "mode", "bars", "mood", "pieces"],
        },
        "music_game": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enabled": {"type": "boolean"},
                "game_type": {"type": "string"},
                "game_name": {"type": "string"},
                "music_concept": {"type": "string"},
                "goal": {"type": "string"},
                "rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "music_element": {"type": "string"},
                            "value": {"type": "string"},
                            "character": {"type": "string"},
                            "motion": {"type": "string"},
                            "feedback": {"type": "string"},
                        },
                        "required": ["music_element", "value", "character", "motion", "feedback"],
                    },
                },
                "student_actions": {"type": "array", "items": {"type": "string"}},
                "win_condition": {"type": "string"},
            },
            "required": ["enabled", "game_type", "game_name", "music_concept", "goal", "rules", "student_actions", "win_condition"],
        },
        "teacher_notes": {"type": "array", "items": {"type": "string"}},
        "blueprint_plan": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "blueprint_id": {"type": "string"},
                "blueprint_label": {"type": "string"},
                "selection_reason": {"type": "string"},
                "primary_interaction": {"type": "string"},
                "gameplay_focus": {"type": "string"},
                "progression_strategy": {"type": "string"},
                "component_focus": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "blueprint_id",
                "blueprint_label",
                "selection_reason",
                "primary_interaction",
                "gameplay_focus",
                "progression_strategy",
                "component_focus",
            ],
        },
        "generation_strategy": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "mode": {"type": "string"},
                "artifact_goal": {"type": "string"},
                "opencode_execution_target": {"type": "string"},
                "prefer_incremental_revision": {"type": "boolean"},
                "render_priority": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "mode",
                "artifact_goal",
                "opencode_execution_target",
                "prefer_incremental_revision",
                "render_priority",
            ],
        },
        "interaction_model": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "primary": {"type": "string"},
                "components": {"type": "array", "items": {"type": "string"}},
                "student_actions": {"type": "array", "items": {"type": "string"}},
                "teacher_controls": {"type": "array", "items": {"type": "string"}},
                "artifact_outputs": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["primary", "components", "student_actions", "teacher_controls", "artifact_outputs"],
        },
        "scoring": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enabled": {"type": "boolean"},
                "pass_score": {"type": "integer"},
                "feedback_mode": {"type": "string"},
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "weight": {"type": "number"},
                            "feedback": {"type": "string"},
                        },
                        "required": ["id", "label", "weight", "feedback"],
                    },
                },
            },
            "required": ["enabled", "pass_score", "feedback_mode", "metrics"],
        },
        "runtime_behaviors": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "save_progress": {"type": "boolean"},
                "unlock_next_step": {"type": "boolean"},
                "countdown": {"type": "boolean"},
                "auto_play_after_start": {"type": "boolean"},
                "resettable": {"type": "boolean"},
                "allow_teacher_override": {"type": "boolean"},
                "allow_continue_revision": {"type": "boolean"},
                "requires_audio_upload": {"type": "boolean"},
                "playback": {"type": "string"},
            },
            "required": [
                "save_progress",
                "unlock_next_step",
                "countdown",
                "auto_play_after_start",
                "resettable",
                "allow_teacher_override",
                "allow_continue_revision",
                "requires_audio_upload",
                "playback",
            ],
        },
        "visual_theme": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "mood": {"type": "string"},
                "layout": {"type": "string"},
                "palette": {"type": "array", "items": {"type": "string"}},
                "illustration_style": {"type": "string"},
                "motion": {"type": "string"},
            },
            "required": ["name", "mood", "layout", "palette", "illustration_style", "motion"],
        },
    },
    "required": [
        "activity_type",
        "title",
        "subtitle",
        "grade_band",
        "song_name",
        "selected_skills",
        "listening",
        "performance",
        "creation",
        "music_game",
        "teacher_notes",
        "blueprint_plan",
        "generation_strategy",
        "interaction_model",
        "scoring",
        "runtime_behaviors",
        "visual_theme",
    ],
}


class ModelGateway:
    def provider_status(self) -> dict[str, Any]:
        llm_config = llm_runtime_config()
        return {
            "ollama": {
                "enabled": bool(os.getenv("OLLAMA_MODEL")),
                "model": os.getenv("OLLAMA_MODEL", ""),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            },
            "openai_responses": {
                "enabled": bool(os.getenv("OPENAI_API_KEY")),
                "model": os.getenv("OPENAI_MODEL", "gpt-5"),
            },
            "openai_compatible": {
                "enabled": llm_config["enabled"],
                "model": llm_config["model"],
                "base_url": llm_config["base_url"],
                "provider": llm_config["provider"],
            },
            "local_fallback": {"enabled": True, "model": "rule-based-music-agent"},
        }

    def generate_tool_spec(
        self,
        need: str,
        skills: list[dict],
        force_local: bool = False,
        forced_activity_type: str | None = None,
    ) -> tuple[dict, dict]:
        if not force_local and os.getenv("OLLAMA_MODEL"):
            try:
                return self._generate_with_ollama(need, skills, forced_activity_type=forced_activity_type), {
                    "provider": "ollama",
                    "model": os.getenv("OLLAMA_MODEL", ""),
                }
            except Exception as exc:
                spec = self._generate_locally(need, forced_activity_type=forced_activity_type)
                spec["teacher_notes"].append("我先用本地课堂规则帮你生成了这一版，你可以继续对话让我修改。")
                return spec, {"provider": "local_fallback", "model": "rule-based-music-agent", "error": str(exc)}

        if not force_local and os.getenv("OPENAI_API_KEY"):
            try:
                return self._generate_with_openai(need, skills, forced_activity_type=forced_activity_type), {
                    "provider": "openai_responses",
                    "model": os.getenv("OPENAI_MODEL", "gpt-5"),
                }
            except Exception as exc:  # pragma: no cover - 需要真实 API 环境
                spec = self._generate_locally(need, forced_activity_type=forced_activity_type)
                spec["teacher_notes"].append("我先用本地课堂规则帮你生成了这一版，你可以继续对话让我修改。")
                return spec, {"provider": "local_fallback", "model": "rule-based-music-agent", "error": str(exc)}

        llm_config = llm_runtime_config()
        if not force_local and llm_config["enabled"]:
            try:
                return self._generate_with_openai_compatible(need, skills, forced_activity_type=forced_activity_type), {
                    "provider": llm_config["provider"],
                    "model": llm_config["model"],
                }
            except Exception as exc:  # pragma: no cover - 需要真实 API 环境
                spec = self._generate_locally(need, forced_activity_type=forced_activity_type)
                spec["teacher_notes"].append("我先用本地课堂规则帮你生成了这一版，你可以继续对话让我修改。")
                return spec, {"provider": "local_fallback", "model": "rule-based-music-agent", "error": str(exc)}

        return self._generate_locally(need, forced_activity_type=forced_activity_type), {"provider": "local_fallback", "model": "rule-based-music-agent"}

    def guide_generation(self, need: str) -> dict:
        return build_guidance(need).to_dict()

    def build_revision_need(self, current_spec: dict[str, Any], revision: str) -> str:
        activity_type = current_spec.get("activity_type", "mixed")
        activity_label = {
            "listening": "聆听工具",
            "performance": "表现闯关",
            "creation": "创造拼图",
            "music_game": "音乐小游戏",
            "mixed": "完整课堂",
        }.get(activity_type, "音乐课堂工具")
        lines = [
            f"请在当前{activity_label}基础上生成一个修改后的新版。",
            f"原标题：{current_spec.get('title', '音乐课堂工具')}",
            f"原曲目：{current_spec.get('song_name', '自选歌曲')}",
            f"原学段：{current_spec.get('grade_band', '小学')}",
            f"修改要求：{revision}",
            "请尽量保留原有课堂目标和活动结构，只调整用户明确提出的内容。",
        ]

        if activity_type in ("performance", "mixed"):
            levels = current_spec.get("performance", {}).get("levels", [])
            if levels:
                level_titles = "、".join(level.get("title", "") for level in levels[:6] if level.get("title"))
                lines.append(f"原有关卡：{level_titles}")

        if activity_type in ("creation", "mixed"):
            creation = current_spec.get("creation", {})
            lines.append(
                f"原创造设置：主音 {creation.get('tonic', 'C')}，调式 {creation.get('mode', 'western_major')}，小节数 {creation.get('bars', 4)}。"
            )

        if activity_type in ("listening", "mixed"):
            listening = current_spec.get("listening", {})
            lines.append(
                f"原聆听设置：主音 {listening.get('tonic', 'C')}，调式 {listening.get('mode', 'western_major')}，节奏 {listening.get('rhythm_density', 'preserve')}，音色 {listening.get('instrument', 'piano')}。"
            )

        if activity_type == "music_game":
            music_game = current_spec.get("music_game", {})
            rule_summary = "、".join(
                rule.get("music_element", "")
                for rule in music_game.get("rules", [])[:6]
                if isinstance(rule, dict) and rule.get("music_element")
            )
            lines.append(
                f"原游戏设置：玩法 {music_game.get('game_type', '未指定')}，概念 {music_game.get('music_concept', '音乐要素')}，规则 {rule_summary or '未指定'}。"
            )

        interaction = current_spec.get("interaction_model", {})
        if interaction:
            lines.append(
                f"原交互方案：主要玩法 {interaction.get('primary', '未指定')}，组件包含 {'、'.join(interaction.get('components', [])[:6])}。"
            )

        return "\n".join(lines)

    def polish_generation_need(self, need: str) -> tuple[dict[str, str], dict]:
        cleaned_need = re.sub(r"\s+", " ", need).strip()
        if not cleaned_need:
            return {"polished": "", "original": need}, {"provider": "local_fallback", "model": "rule-based-music-agent"}

        if os.getenv("OLLAMA_MODEL"):
            try:
                polished = self._polish_with_ollama(cleaned_need)
                return {"polished": polished, "original": need}, {"provider": "ollama", "model": os.getenv("OLLAMA_MODEL", "")}
            except Exception as exc:
                return {"polished": self._polish_locally(cleaned_need), "original": need}, {
                    "provider": "local_fallback",
                    "model": "rule-based-music-agent",
                    "error": str(exc),
                }

        llm_config = llm_runtime_config()
        if llm_config["enabled"]:
            try:
                polished = self._polish_with_openai_compatible(cleaned_need)
                return {"polished": polished, "original": need}, {"provider": llm_config["provider"], "model": llm_config["model"]}
            except Exception as exc:
                return {"polished": self._polish_locally(cleaned_need), "original": need}, {
                    "provider": "local_fallback",
                    "model": "rule-based-music-agent",
                    "error": str(exc),
                }

        if os.getenv("OPENAI_API_KEY"):
            try:
                polished = self._polish_with_openai(cleaned_need)
                return {"polished": polished, "original": need}, {"provider": "openai_responses", "model": os.getenv("OPENAI_MODEL", "gpt-5")}
            except Exception as exc:
                return {"polished": self._polish_locally(cleaned_need), "original": need}, {
                    "provider": "local_fallback",
                    "model": "rule-based-music-agent",
                    "error": str(exc),
                }

        return {"polished": self._polish_locally(cleaned_need), "original": need}, {
            "provider": "local_fallback",
            "model": "rule-based-music-agent",
        }

    def chat_reply(self, message: str) -> tuple[str, dict]:
        if _is_inspiration_generation_request(message):
            template_id = _matched_production_template_id(message)
            return _inspiration_boundary_reply(message), _with_inspiration_grounding(
                {
                    "provider": "guardrail",
                    "model": "inspiration-assistant-boundary",
                },
                template_id,
            )
        if os.getenv("OLLAMA_MODEL"):
            try:
                reply = _enforce_inspiration_reply_guardrails(message, self._chat_with_ollama(message))
                return reply, _with_inspiration_grounding({"provider": "ollama", "model": os.getenv("OLLAMA_MODEL", "")}, message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    message,
                )

        llm_config = llm_runtime_config()
        if llm_config["enabled"]:
            try:
                reply = _enforce_inspiration_reply_guardrails(message, self._chat_with_openai_compatible(message))
                return reply, _with_inspiration_grounding({"provider": llm_config["provider"], "model": llm_config["model"]}, message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    message,
                )

        if os.getenv("OPENAI_API_KEY"):
            try:
                reply = _enforce_inspiration_reply_guardrails(message, self._chat_with_openai(message))
                return reply, _with_inspiration_grounding({"provider": "openai_responses", "model": os.getenv("OPENAI_MODEL", "gpt-5")}, message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    message,
                )

        return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
            {"provider": "local_fallback", "model": "rule-based-music-agent"},
            message,
        )

    def chat_reply_chat_ecnu_only(self, message: str) -> tuple[str, dict]:
        if _is_inspiration_generation_request(message):
            template_id = _matched_production_template_id(message)
            return _inspiration_boundary_reply(message), _with_inspiration_grounding(
                {
                    "provider": "guardrail",
                    "model": "inspiration-assistant-boundary",
                    "target_provider": "chat_ecnu",
                },
                template_id,
            )
        llm_config = llm_runtime_config()
        if llm_config["enabled"] and llm_config["provider"] == "chat_ecnu":
            try:
                reply = _enforce_inspiration_reply_guardrails(message, self._chat_with_openai_compatible(message))
                return reply, _with_inspiration_grounding({"provider": "chat_ecnu", "model": llm_config["model"]}, message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "target_provider": "chat_ecnu",
                        "error": str(exc),
                    },
                    message,
                )
        return _enforce_inspiration_reply_guardrails(message, self._chat_locally(message)), _with_inspiration_grounding(
            {
                "provider": "local_fallback",
                "model": "rule-based-music-agent",
                "target_provider": "chat_ecnu",
                "error": "ChatECNU 未启用",
            },
            message,
        )

    def chat_reply_with_history(self, messages: list[dict[str, str]]) -> tuple[str, dict]:
        latest_user_message = _latest_user_message(messages)
        if _is_inspiration_generation_request(latest_user_message):
            template_id = _matched_production_template_id(latest_user_message)
            return _inspiration_boundary_reply(latest_user_message), _with_inspiration_grounding(
                {
                    "provider": "guardrail",
                    "model": "inspiration-assistant-boundary",
                },
                template_id,
            )
        if os.getenv("OLLAMA_MODEL"):
            try:
                reply = _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_with_ollama_messages(messages))
                return reply, _with_inspiration_grounding({"provider": "ollama", "model": os.getenv("OLLAMA_MODEL", "")}, latest_user_message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    latest_user_message,
                )

        llm_config = llm_runtime_config()
        if llm_config["enabled"]:
            try:
                reply = _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_with_openai_compatible_messages(messages))
                return reply, _with_inspiration_grounding({"provider": llm_config["provider"], "model": llm_config["model"]}, latest_user_message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    latest_user_message,
                )

        if os.getenv("OPENAI_API_KEY"):
            try:
                reply = _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_with_openai_messages(messages))
                return reply, _with_inspiration_grounding({"provider": "openai_chat", "model": os.getenv("OPENAI_MODEL", "gpt-5")}, latest_user_message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "error": str(exc),
                    },
                    latest_user_message,
                )

        return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
            {
                "provider": "local_fallback",
                "model": "rule-based-music-agent",
            },
            latest_user_message,
        )

    def chat_reply_chat_ecnu_only_with_history(self, messages: list[dict[str, str]]) -> tuple[str, dict]:
        latest_user_message = _latest_user_message(messages)
        if _is_inspiration_generation_request(latest_user_message):
            template_id = _matched_production_template_id(latest_user_message)
            return _inspiration_boundary_reply(latest_user_message), _with_inspiration_grounding(
                {
                    "provider": "guardrail",
                    "model": "inspiration-assistant-boundary",
                    "target_provider": "chat_ecnu",
                },
                template_id,
            )
        llm_config = llm_runtime_config()
        if llm_config["enabled"] and llm_config["provider"] == "chat_ecnu":
            try:
                reply = _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_with_openai_compatible_messages(messages))
                return reply, _with_inspiration_grounding({"provider": "chat_ecnu", "model": llm_config["model"]}, latest_user_message)
            except Exception as exc:
                return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
                    {
                        "provider": "local_fallback",
                        "model": "rule-based-music-agent",
                        "target_provider": "chat_ecnu",
                        "error": str(exc),
                    },
                    latest_user_message,
                )
        return _enforce_inspiration_reply_guardrails(latest_user_message, self._chat_locally(latest_user_message)), _with_inspiration_grounding(
            {
                "provider": "local_fallback",
                "model": "rule-based-music-agent",
                "target_provider": "chat_ecnu",
                "error": "ChatECNU 未启用",
            },
            latest_user_message,
        )

    def _generate_with_ollama(self, need: str, skills: list[dict], *, forced_activity_type: str | None = None) -> dict:
        response_text = self._ollama_chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._build_user_prompt(need, skills)},
            ],
            json_mode=True,
        )
        return self._coerce_spec(_json_from_text(response_text), need=need, forced_activity_type=forced_activity_type)

    def _generate_with_openai(self, need: str, skills: list[dict], *, forced_activity_type: str | None = None) -> dict:
        from openai import OpenAI

        client = OpenAI(http_client=self._openai_http_client())
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            instructions=SYSTEM_PROMPT,
            input=self._build_user_prompt(need, skills),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "music_classroom_tool_spec",
                    "schema": TOOL_SPEC_SCHEMA,
                    "strict": True,
                }
            },
        )
        return self._coerce_spec(_json_from_text(response.output_text), need=need, forced_activity_type=forced_activity_type)

    def _generate_with_openai_compatible(
        self,
        need: str,
        skills: list[dict],
        *,
        forced_activity_type: str | None = None,
    ) -> dict:
        from openai import OpenAI

        llm_config = llm_runtime_config()
        client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            http_client=self._openai_http_client(),
        )
        response = client.chat.completions.create(
            model=llm_config["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._build_user_prompt(need, skills)},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return self._coerce_spec(_json_from_text(content), need=need, forced_activity_type=forced_activity_type)

    def _chat_with_ollama(self, message: str) -> str:
        return self._ollama_chat(
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "system", "content": _inspiration_request_grounding_context(message)},
                {"role": "user", "content": message},
            ],
            json_mode=False,
        ).strip()

    def _chat_with_ollama_messages(self, messages: list[dict[str, str]]) -> str:
        latest_user_message = _latest_user_message(messages)
        return self._ollama_chat(
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "system", "content": _inspiration_request_grounding_context(latest_user_message)},
                *messages,
            ],
            json_mode=False,
        ).strip()

    def _chat_with_openai(self, message: str) -> str:
        from openai import OpenAI

        client = OpenAI(http_client=self._openai_http_client())
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            instructions=f"{CHAT_SYSTEM_PROMPT}\n\n{_inspiration_request_grounding_context(message)}",
            input=message,
        )
        return response.output_text.strip()

    def _chat_with_openai_messages(self, messages: list[dict[str, str]]) -> str:
        from openai import OpenAI

        client = OpenAI(http_client=self._openai_http_client())
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "system", "content": _inspiration_request_grounding_context(_latest_user_message(messages))},
                *messages,
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _chat_with_openai_compatible(self, message: str) -> str:
        from openai import OpenAI

        llm_config = llm_runtime_config()
        client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            http_client=self._openai_http_client(),
        )
        response = client.chat.completions.create(
            model=llm_config["model"],
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "system", "content": _inspiration_request_grounding_context(message)},
                {"role": "user", "content": message},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _chat_with_openai_compatible_messages(self, messages: list[dict[str, str]]) -> str:
        from openai import OpenAI

        llm_config = llm_runtime_config()
        client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            http_client=self._openai_http_client(),
        )
        response = client.chat.completions.create(
            model=llm_config["model"],
            messages=[
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                {"role": "system", "content": _inspiration_request_grounding_context(_latest_user_message(messages))},
                *messages,
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def _polish_with_ollama(self, need: str) -> str:
        return self._clean_polished_text(
            self._ollama_chat(
                messages=[
                    {"role": "system", "content": POLISH_SYSTEM_PROMPT},
                    {"role": "user", "content": need},
                ],
                json_mode=False,
            )
        )

    def _polish_with_openai(self, need: str) -> str:
        from openai import OpenAI

        client = OpenAI(http_client=self._openai_http_client())
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            instructions=POLISH_SYSTEM_PROMPT,
            input=need,
        )
        return self._clean_polished_text(response.output_text)

    def _polish_with_openai_compatible(self, need: str) -> str:
        from openai import OpenAI

        llm_config = llm_runtime_config()
        client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
            http_client=self._openai_http_client(),
        )
        response = client.chat.completions.create(
            model=llm_config["model"],
            messages=[
                {"role": "system", "content": POLISH_SYSTEM_PROMPT},
                {"role": "user", "content": need},
            ],
        )
        return self._clean_polished_text(response.choices[0].message.content or "")

    def _ollama_chat(self, messages: list[dict], json_mode: bool) -> str:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        payload: dict[str, Any] = {
            "model": os.environ["OLLAMA_MODEL"],
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            },
        }
        if json_mode:
            payload["format"] = "json"

        request = urllib.request.Request(
            f"{base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=float(os.getenv("OLLAMA_TIMEOUT", "90"))) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama 服务不可用：{exc}") from exc

        content = body.get("message", {}).get("content", "")
        if not content:
            raise RuntimeError("Ollama 没有返回可用内容。")
        return content

    def _build_user_prompt(self, need: str, skills: list[dict]) -> str:
        knowledge_context = compact_prompt_context(need)
        return "\n".join(
            [
                f"教师需求：{need}",
                "音乐教育知识库上下文：",
                json.dumps(knowledge_context, ensure_ascii=False, indent=2),
                "可调用 skill：",
                json.dumps(skills, ensure_ascii=False, indent=2),
                "可组合交互组件库：",
                json.dumps(component_prompt_catalog(), ensure_ascii=False, indent=2),
                "请只输出符合 schema 的 JSON。",
            ]
        )

    def _polish_locally(self, need: str) -> str:
        activity_type = self._infer_activity_type(need)
        song_name = self._infer_song_name(need)
        grade_band = "小学" if "小学" in need else "初中" if "初中" in need else "高中" if "高中" in need else "小学"
        activity_label = {
            "listening": "聆听对比工具",
            "performance": "表现闯关工具",
            "creation": "创造拼图工具",
            "music_game": "音乐小游戏",
            "mixed": "综合音乐课堂工具",
        }[activity_type]
        song_part = f"围绕《{song_name}》" if song_name != "自选歌曲" else "围绕自选音乐素材"

        if activity_type == "listening":
            detail = "支持学生上传音频后进行调式、节奏、速度和音色对比，帮助学生说清音乐要素带来的听觉变化。"
        elif activity_type == "performance":
            stage_count = self._infer_stage_count(need, 4)
            detail = f"设计 {stage_count} 个循序渐进的关卡，包含听辨、模仿、合作表现和展示评价，便于课堂分组完成。"
        elif activity_type == "creation":
            detail = "提供可拖拽的音乐素材和网格旋律线，引导学生拼接、试听并说明自己的创作想法。"
        elif activity_type == "music_game":
            detail = "把音乐概念变成可操作的小游戏，包含角色、规则、反馈、重新挑战和课堂讨论提示。"
        else:
            detail = "依次安排聆听、表现和创造任务，形成从感知到展示再到创编的完整课堂活动。"

        return f"请生成一个适合{grade_band}学生使用的{activity_label}，{song_part}开展课堂活动。{detail}"

    def _clean_polished_text(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"^润色后[：:]\s*", "", cleaned)
        cleaned = cleaned.strip("「」\"'")
        return cleaned

    def _chat_locally(self, message: str) -> str:
        template_id = _matched_production_template_id(message)
        if template_id:
            label = INSPIRATION_TEMPLATE_LABELS.get(template_id, template_id)
            reason = INSPIRATION_TEMPLATE_REASONS.get(template_id, "这个方向和当前内置模板比较接近。")
            return (
                f"这个想法可以聊，而且比较接近“{label}”方向。{reason}"
                "如果你愿意，我会再帮你把年级、曲目、学生动作和通关表达补清楚，再放进生成框。"
            )
        if _mentions_unsupported_expression_template(message):
            return _template_grounded_inspiration_reply(message)
        if any(keyword in message for keyword in ["你好", "嗨", "hello"]):
            return "你好，我在。你可以先随便说一个课堂难点，我会帮你判断更适合听辨、表现、创编，还是小游戏。"
        if any(keyword in message for keyword in ["网页", "工具", "生成", "制作"]):
            guidance = build_guidance(message)
            if guidance.ready:
                return "这些信息基本够用了。我建议再确认一下学生最后要说、唱还是拍出来；确认后就可以放入生成框。"
            return guidance.question
        if any(keyword in message for keyword in ["调式", "调性", "节奏", "速度", "音色"]):
            return "可以把它整理成聆听活动：上传音频，选择调式、节奏、速度和音色，再做前后对比。"
        if any(keyword in message for keyword in ["小游戏", "游戏", "赛跑", "翻牌", "消消乐"]):
            return "可以做成音乐小游戏：先把音乐概念变成规则，再安排角色、学生操作、即时反馈和重新挑战。"
        if any(keyword in message for keyword in ["闯关", "表现"]):
            return "我可以把目标拆成一关一关的小挑战，让学生先听辨，再模仿，再合作展示，难度会慢慢升级。"
        if any(keyword in message for keyword in ["拼图", "创造", "创编"]):
            return "创造层我会把音高、节奏和结构功能变成可拖拽的小拼图，学生可以拼成自己的小曲子。"
        return "我在。你可以告诉我想生成哪类音乐工具产物，并补充学段、曲目、互动目标和关卡或创作规则。"

    def _generate_locally(self, need: str, *, forced_activity_type: str | None = None) -> dict:
        plan = generate_agent_plan(need)
        activity_type = forced_activity_type if forced_activity_type in {"listening", "performance", "creation", "music_game", "mixed"} else self._infer_activity_type(need)
        stage_count = self._infer_stage_count(need, plan["performance"]["stage_count"])
        mood = self._infer_mood(need, plan["creation"]["mood"])
        performance = generate_game_plan(
            GameRequest(
                stage_count=stage_count,
                grade_band=plan["performance"]["grade_band"],
                target_skill=plan["performance"]["target_skill"],
                theme=self._infer_theme_or_song(need, plan["performance"]["theme"]),
            )
        )
        performance_levels = self._extract_user_levels(
            need=need,
            fallback_levels=performance["levels"],
            target_skill=performance["target_skill"],
        )
        if performance_levels:
            stage_count = len(performance_levels)
        creation = generate_creation_puzzle(
            PuzzleRequest(
                tonic=plan["creation"]["tonic"],
                mode=plan["creation"]["mode"],
                bars=plan["creation"]["bars"],
                mood=mood,
            )
        )

        return self._coerce_spec(
            {
                "activity_type": activity_type,
                "title": self._build_title(need, activity_type),
                "subtitle": self._build_subtitle(activity_type),
                "grade_band": plan["performance"]["grade_band"],
                "song_name": self._infer_song_name(need),
                "selected_skills": self._skills_for_activity(activity_type),
                "original_user_need": need.strip(),
                "user_prompt_contract": self._prompt_contract_for_need(need, activity_type),
                "listening": {
                    "enabled": activity_type in ("listening", "mixed"),
                    **plan["listening"],
                    "task": "上传音频后直接选择音乐要素，页面会自动把音乐变成新的课堂版本。",
                },
                "performance": {
                    "enabled": activity_type in ("performance", "mixed"),
                    "theme": performance["theme"],
                    "target_skill": performance["target_skill"],
                    "stage_count": stage_count,
                    "levels": performance_levels,
                },
                "creation": {
                    "enabled": activity_type in ("creation", "mixed"),
                    "tonic": plan["creation"]["tonic"],
                    "mode": plan["creation"]["mode"],
                    "bars": plan["creation"]["bars"],
                    "mood": mood,
                    "creation_mode": self._infer_creation_mode(need),
                    "pieces": creation["pieces"],
                },
                "music_game": self._music_game_for_need(need, activity_type),
                "teacher_notes": self._teacher_notes_for_activity(activity_type),
                "blueprint_plan": self._blueprint_plan_for_need(need, activity_type),
                "generation_strategy": self._generation_strategy_for_need(need, activity_type),
                "interaction_model": self._interaction_model_for_activity(need, activity_type),
                "scoring": self._scoring_for_activity(need, activity_type),
                "runtime_behaviors": self._runtime_behaviors_for_activity(need, activity_type),
                "visual_theme": self._visual_theme_for_need(need, activity_type),
            },
            need=need,
            forced_activity_type=forced_activity_type,
        )

    def _coerce_spec(self, spec: dict, *, need: str = "", forced_activity_type: str | None = None) -> dict:
        allowed_activity_types = {"listening", "performance", "creation", "music_game", "mixed"}
        if forced_activity_type in allowed_activity_types:
            spec["activity_type"] = forced_activity_type
        else:
            activity_type = spec.get("activity_type") or "mixed"
            spec["activity_type"] = activity_type if activity_type in allowed_activity_types else "mixed"
            if self._should_force_listening_from_need(need):
                spec["activity_type"] = "listening"
        spec.setdefault("title", "音乐课堂网页工具")
        spec.setdefault("subtitle", "根据教师需求生成的互动课堂工具。")
        spec.setdefault("grade_band", "小学")
        spec.setdefault("song_name", "自选歌曲")
        spec["selected_skills"] = self._skills_for_activity(spec["activity_type"])
        spec.setdefault("teacher_notes", [])
        spec.setdefault("listening", {})
        spec.setdefault("performance", {})
        spec.setdefault("creation", {})
        spec.setdefault("music_game", {})
        spec.setdefault("interaction_model", {})
        spec.setdefault("scoring", {})
        spec.setdefault("runtime_behaviors", {})
        spec.setdefault("visual_theme", {})
        spec.setdefault("blueprint_plan", {})
        spec.setdefault("generation_strategy", {})
        if need.strip():
            spec["original_user_need"] = need.strip()
        spec["user_prompt_contract"] = self._coerce_prompt_contract(spec, need=need)
        spec = apply_generation_mode(spec, spec["activity_type"])

        plan = generate_agent_plan(spec["title"] + spec["subtitle"])
        spec["listening"] = {
            "enabled": spec["activity_type"] in ("listening", "mixed"),
            "engine": "Blueprint_Listen",
            "tonic": spec["listening"].get("tonic", plan["listening"]["tonic"]),
            "mode": self._normalize_listening_mode(spec["listening"].get("mode", plan["listening"]["mode"])),
            "tempo_multiplier": float(spec["listening"].get("tempo_multiplier", plan["listening"]["tempo_multiplier"])),
            "rhythm_density": self._normalize_rhythm_density(
                spec["listening"].get("rhythm_density", plan["listening"]["rhythm_density"])
            ),
            "instrument": self._normalize_listening_instrument(
                spec["listening"].get("instrument", plan["listening"]["instrument"])
            ),
            "task": spec["listening"].get("task", "上传音频并选择音乐要素，让音乐变成新的课堂版本。"),
        }
        spec["performance"] = {
            "enabled": spec["activity_type"] in ("performance", "mixed"),
            "controller_type": "Blueprint_Performance.LevelController",
            "theme": spec["performance"].get("theme", "音乐探险"),
            "target_skill": spec["performance"].get("target_skill", "音乐要素综合感知"),
            "stage_count": int(spec["performance"].get("stage_count", 4)),
            "levels": spec["performance"].get("levels", []),
        }
        if not spec["performance"]["levels"]:
            fallback_game = generate_game_plan(
                GameRequest(
                    stage_count=max(3, min(spec["performance"]["stage_count"], 6)),
                    grade_band=spec["grade_band"],
                    target_skill=spec["performance"]["target_skill"],
                    theme=spec["performance"]["theme"],
                )
            )
            spec["performance"]["levels"] = [
                {
                    "title": level["title"],
                    "goal": level["goal"],
                    "student_task": level["student_task"],
                    "success_rule": level["success_rule"],
                }
                for level in fallback_game["levels"]
            ]

        spec["creation"] = {
            "enabled": spec["activity_type"] in ("creation", "mixed"),
            "asset_loader": "Blueprint_Creation.AssetLoader",
            "creation_mode": spec["creation"].get(
                "creation_mode",
                self._infer_creation_mode(spec["title"] + spec["subtitle"] + spec["creation"].get("mood", "")),
            ),
            "tonic": spec["creation"].get("tonic", plan["creation"]["tonic"]),
            "mode": spec["creation"].get("mode", plan["creation"]["mode"]),
            "bars": int(spec["creation"].get("bars", plan["creation"]["bars"])),
            "mood": spec["creation"].get("mood", plan["creation"]["mood"]),
            "pieces": spec["creation"].get("pieces", []),
        }
        if not spec["creation"]["pieces"]:
            puzzle = generate_creation_puzzle(
                PuzzleRequest(
                    tonic=spec["creation"]["tonic"],
                    mode=spec["creation"]["mode"],
                    bars=spec["creation"]["bars"],
                    mood=spec["creation"]["mood"],
                )
            )
            spec["creation"]["pieces"] = puzzle["pieces"]

        spec["music_game"] = self._coerce_music_game(spec)

        if not spec["teacher_notes"]:
            spec["teacher_notes"] = self._teacher_notes_for_activity(spec["activity_type"])

        spec["blueprint_plan"] = self._coerce_blueprint_plan(spec, need=need)
        spec["generation_strategy"] = self._coerce_generation_strategy(spec, need=need)
        spec["interaction_model"] = self._coerce_interaction_model(spec)
        spec["scoring"] = self._coerce_scoring(spec)
        spec["runtime_behaviors"] = self._coerce_runtime_behaviors(spec)
        spec["visual_theme"] = self._coerce_visual_theme(spec)
        spec = attach_music_logic_contract(spec, need=need)

        return spec

    def _infer_activity_type(self, need: str) -> str:
        activity_type = infer_activity_type(need)
        return "mixed" if activity_type == "unknown" else activity_type

    def _should_force_listening_from_need(self, need: str) -> bool:
        text = re.sub(r"\s+", " ", str(need or "").lower())
        if not text:
            return False
        if any(token in text for token in ["音乐小游戏", "小游戏", "闯关", "创造", "创作", "拼图", "拖拽"]):
            return False
        return any(
            token in text
            for token in [
                "聆听工具",
                "听辨工具",
                "上传音频",
                "切换音乐要素",
                "音乐要素修改",
                "要素修改",
                "转midi",
                "转 midi",
                "改音",
                "改节奏",
                "对比试听",
            ]
        )

    def _normalize_rhythm_density(self, value: Any) -> str:
        normalized = str(value or "preserve").strip()
        return normalized if normalized in {"preserve", "dense", "relaxed"} else "preserve"

    def _normalize_listening_mode(self, value: Any) -> str:
        normalized = str(value or "preserve").strip()
        valid_modes = {
            "preserve",
            "western_major",
            "western_minor",
            "chinese_pentatonic",
            "chinese_heptatonic",
            "dorian",
            "phrygian",
            "blues",
        }
        return normalized if normalized in valid_modes else "preserve"

    def _normalize_listening_instrument(self, value: Any) -> str:
        normalized = str(value or "preserve").strip()
        return normalized if normalized in {"preserve", "piano", "violin", "flute", "guzheng"} else "preserve"

    def _skills_for_activity(self, activity_type: str) -> list[str]:
        if activity_type == "listening":
            return ["listening_basic_pitch", "webpage_composer"]
        if activity_type == "performance":
            return ["performance_game", "webpage_composer"]
        if activity_type == "creation":
            return ["creation_puzzle", "webpage_composer"]
        if activity_type == "music_game":
            return ["music_game_builder", "webpage_composer"]
        return ["listening_basic_pitch", "performance_game", "creation_puzzle", "webpage_composer"]

    def _infer_song_name(self, need: str) -> str:
        bracket_match = re.search(r"《([^》]{1,40})》", need)
        if bracket_match:
            return bracket_match.group(1).strip()

        markers = ["歌曲", "曲目", "作品", "用"]
        for marker in markers:
            if marker in need:
                tail = need.split(marker, 1)[1].strip(" ：:，,。")
                if tail:
                    return tail.split("，")[0].split(",")[0].split("。")[0][:24]
        return "自选歌曲"

    def _infer_stage_count(self, need: str, fallback: int) -> int:
        digit_match = re.search(r"(\d+)\s*[个道]?关", need)
        if digit_match:
            return max(3, min(int(digit_match.group(1)), 6))

        chinese_numbers = {
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
        }
        for word, value in chinese_numbers.items():
            if f"{word}关" in need or f"{word}个关" in need or f"{word}道关" in need:
                return value
        return fallback

    def _extract_user_levels(self, need: str, fallback_levels: list[dict], target_skill: str) -> list[dict]:
        matches = re.findall(r"第([一二三四五六七八九十0-9]+)关[：:、\s]*([^，,。；;\n]+)", need)
        if not matches:
            return [
                {
                    "title": level["title"],
                    "goal": level["goal"],
                    "student_task": level["student_task"],
                    "success_rule": level["success_rule"],
                }
                for level in fallback_levels
            ]

        levels = []
        for index, (_raw_number, task) in enumerate(matches, start=1):
            clean_task = task.strip(" ：:，,。；;")
            title_task = clean_task or f"{target_skill}挑战"
            levels.append(
                {
                    "title": f"第{index}关：{title_task}",
                    "goal": f"围绕“{title_task}”完成一次清晰可观察的表现训练。",
                    "student_task": f"学生用演唱、律动或课堂乐器完成“{title_task}”，并听同伴反馈再试一次。",
                    "success_rule": "能稳定完成本关要求，并能说出自己改进了哪里即可通关。",
                }
            )
        return levels

    def coerce_music_game(self, spec: dict) -> dict:
        return self._coerce_music_game(spec)

    def _coerce_music_game(self, spec: dict) -> dict:
        provided = spec.get("music_game") if isinstance(spec.get("music_game"), dict) else {}
        lesson_context = spec.get("lesson_context") if isinstance(spec.get("lesson_context"), dict) else {}
        generated = (
            self._music_game_for_lesson_context(lesson_context, spec)
            if lesson_context
            else self._music_game_for_need(
                " ".join(
                    [
                        str(spec.get("title", "")),
                        str(spec.get("subtitle", "")),
                        str(provided.get("game_name", "")),
                        str(provided.get("music_concept", "")),
                        str(provided.get("goal", "")),
                    ]
                ),
                spec["activity_type"],
            )
        )

        target_music_element = str(
            spec.get("target_music_element") or lesson_context.get("target_music_element") or generated.get("music_concept", "")
        )
        target_objective = str(spec.get("target_objective") or lesson_context.get("target_objective") or generated.get("goal", ""))
        target_stage = str(spec.get("target_stage") or lesson_context.get("target_stage") or "")
        provided_rules = provided.get("rules") if isinstance(provided.get("rules"), list) else []
        if lesson_context and not self._rules_align_with_target(provided_rules, target_music_element):
            rules = generated["rules"]
        else:
            rules = provided_rules or generated["rules"]

        clean_rules = []
        for index, rule in enumerate(rules, start=1):
            if not isinstance(rule, dict):
                continue
            if _is_meta_lesson_check(str(rule.get("value", ""))):
                continue
            clean_rules.append(
                {
                    "music_element": str(rule.get("music_element") or f"规则{index}"),
                    "value": str(rule.get("value") or "1拍"),
                    "character": str(rule.get("character") or f"角色{index}"),
                    "motion": str(rule.get("motion") or "按节拍前进"),
                    "feedback": str(rule.get("feedback") or "完成后给出鼓励反馈。"),
                }
            )

        game_name = str(provided.get("game_name") or generated["game_name"])
        if lesson_context and not self._text_targets_lesson(game_name, target_music_element, target_objective):
            game_name = str(generated["game_name"])

        win_condition = str(provided.get("win_condition") or generated["win_condition"])
        if lesson_context and not self._text_targets_lesson(win_condition, target_music_element, target_objective):
            win_condition = str(generated["win_condition"])

        student_actions = _string_list(provided.get("student_actions"), generated["student_actions"])
        action_source = " ".join(
            [
                str(spec.get("original_user_need", "")),
                str(provided.get("mechanic", "")),
                " ".join(str(rule.get("value", "")) for rule in clean_rules if isinstance(rule, dict)),
            ]
        )
        if self._is_pitch_action_response(action_source, target_music_element):
            student_actions = self._pitch_action_response_actions(target_stage)
        if lesson_context and not any(self._text_targets_lesson(action, target_music_element, target_objective) for action in student_actions):
            student_actions = generated["student_actions"]

        game_type = canonical_game_type(str(generated["game_type"] if lesson_context else provided.get("game_type") or generated["game_type"]))
        blueprint = build_music_game_blueprint(
            game_type=game_type,
            concept=str(target_music_element or provided.get("music_concept") or generated["music_concept"]),
            goal=str(target_objective or provided.get("goal") or generated["goal"]),
            stage=str(spec.get("target_stage") or lesson_context.get("target_stage") or ""),
            source_name=game_name,
        )
        result = {
            "enabled": spec["activity_type"] == "music_game",
            "game_type": game_type,
            "game_family": blueprint["game_family"],
            "activity_fit": blueprint.get("activity_fit", []),
            "preferred_activity": blueprint.get("preferred_activity", ""),
            "source_game_forms": blueprint.get("source_game_forms", []),
            "learning_depth": blueprint.get("learning_depth", []),
            "game_name": game_name,
            "music_concept": str(target_music_element or provided.get("music_concept") or generated["music_concept"]),
            "goal": str(target_objective or provided.get("goal") or generated["goal"]),
            "mechanic": str(provided.get("mechanic") or generated.get("mechanic") or blueprint["mechanic"]),
            "rules": clean_rules or generated["rules"],
            "student_actions": student_actions,
            "core_loop": blueprint["core_loop"] if lesson_context else _string_list(provided.get("core_loop"), blueprint["core_loop"]),
            "failure_state": str(provided.get("failure_state") or blueprint["failure_state"]),
            "progression": _string_list(provided.get("progression"), blueprint["progression"]),
            "target_session_minutes": str(provided.get("target_session_minutes") or blueprint["target_session_minutes"]),
            "win_condition": win_condition,
        }
        contract_spec = {
            **spec,
            "music_game": {
                **result,
                "playable_game": provided.get("playable_game", generated.get("playable_game", {})),
            },
        }
        result["music_logic_contract"] = build_music_logic_contract(
            spec=contract_spec,
            need=" ".join(
                [
                    str(spec.get("original_user_need", "")),
                    str(spec.get("title", "")),
                    str(spec.get("subtitle", "")),
                    str(target_music_element),
                ]
            ),
            music_game=contract_spec["music_game"],
            playable_game=contract_spec["music_game"].get("playable_game", {}),
            lesson_context=lesson_context,
        )
        return result

    def _music_game_for_lesson_context(self, lesson_context: dict[str, Any], spec: dict[str, Any]) -> dict:
        target_music_element = str(lesson_context.get("target_music_element") or spec.get("target_music_element") or "音乐要素")
        target_objective = str(lesson_context.get("target_objective") or spec.get("target_objective") or f"围绕“{target_music_element}”完成课堂任务。")
        target_stage = str(lesson_context.get("target_stage") or spec.get("target_stage") or "课堂核心环节")
        target_segment_task = str(lesson_context.get("target_segment_task") or spec.get("target_segment_task") or "")
        target_segment_gameable_point = str(
            lesson_context.get("target_segment_gameable_point") or spec.get("target_segment_gameable_point") or ""
        )
        target_segment_mechanic = str(
            lesson_context.get("target_segment_mechanic") or spec.get("target_segment_mechanic") or ""
        )
        fit_reason = str(
            lesson_context.get("why_this_game_fits_this_lesson")
            or spec.get("why_this_game_fits_this_lesson")
            or lesson_context.get("stage_reason")
            or ""
        )
        need = " ".join(
            [
                target_music_element,
                target_objective,
                target_stage,
                target_segment_task,
                target_segment_gameable_point,
                target_segment_mechanic,
                fit_reason,
                str(lesson_context.get("recommended_game_name", "")),
                str(lesson_context.get("recommended_game_mechanic", "")),
            ]
        ).strip()
        recommended_type = str(lesson_context.get("recommended_game_type") or "")
        game_type = canonical_game_type(recommended_type) if recommended_type else self._infer_lesson_game_type(need)
        template_match = detect_template_match_from_text(
            " ".join(
                [
                    recommended_type,
                    str(lesson_context.get("recommended_game_name", "")),
                    str(lesson_context.get("recommended_game_mechanic", "")),
                    target_segment_task,
                    target_segment_gameable_point,
                ]
            )
        )
        confirmed_rules = [
            str(rule).strip()
            for rule in (lesson_context.get("recommended_game_rules") or [])
            if str(rule).strip() and not _is_meta_lesson_check(str(rule))
        ]
        rules = (
            [{"music_element": target_music_element, "value": str(rule), "character": "课堂任务卡", "motion": "按确认规则完成", "feedback": "说出音乐理由。"} for rule in confirmed_rules[:5]]
            if isinstance(confirmed_rules, list) and confirmed_rules
            else self._music_game_rules_for_lesson_context(target_music_element, target_objective, target_stage)
        )
        confirmed_actions = lesson_context.get("recommended_game_actions") or []
        student_actions = (
            [str(action) for action in confirmed_actions[:6] if str(action).strip()]
            if isinstance(confirmed_actions, list) and confirmed_actions
            else self._music_game_actions_for_lesson_context(target_music_element, target_stage)
        )
        blueprint = build_music_game_blueprint(
            game_type=game_type,
            concept=target_music_element,
            goal=target_objective,
            stage=target_stage,
            source_name=str(lesson_context.get("recommended_game_name") or ""),
        )
        return {
            "enabled": True,
            "game_type": game_type,
            "matched_template_id": template_match,
            "game_family": blueprint["game_family"],
            "activity_fit": blueprint.get("activity_fit", []),
            "preferred_activity": blueprint.get("preferred_activity", ""),
            "source_game_forms": blueprint.get("source_game_forms", []),
            "learning_depth": blueprint.get("learning_depth", []),
            "game_name": str(lesson_context.get("recommended_game_name") or f"{target_music_element}课堂挑战"),
            "music_concept": target_music_element,
            "goal": target_objective,
            "mechanic": str(lesson_context.get("recommended_game_mechanic") or target_segment_mechanic or blueprint["mechanic"]),
            "rules": rules,
            "student_actions": student_actions,
            "core_loop": blueprint["core_loop"],
            "failure_state": blueprint["failure_state"],
            "progression": blueprint["progression"],
            "target_session_minutes": blueprint["target_session_minutes"],
            "target_segment_task": target_segment_task,
            "target_segment_gameable_point": target_segment_gameable_point,
            "target_segment_mechanic": target_segment_mechanic,
            "selected_segment": lesson_context.get("selected_game_segment", {}),
            "goal_task_game_mapping": lesson_context.get("goal_task_game_mapping", [])[:3],
            "win_condition": f"学生完成“{target_music_element}”相关挑战后，能说明这怎样服务“{target_objective}”。",
        }

    def _infer_lesson_game_type(self, target_music_element: str) -> str:
        return infer_game_type_from_text(target_music_element)

    def _music_game_rules_for_lesson_context(self, target_music_element: str, target_objective: str, target_stage: str) -> list[dict[str, str]]:
        if any(word in target_music_element for word in ["sol", "mi", "唱名", "高低音", "5音", "3音"]):
            return [
                {"music_element": "sol", "value": "较高的唱名", "character": "小太阳", "motion": "放到更高的音高台阶", "feedback": "sol 是这组材料里较高的那个音。"},
                {"music_element": "mi", "value": "较低的唱名", "character": "小叶子", "motion": "放到较低的音高台阶", "feedback": "mi 是这组材料里较低的那个音。"},
                {"music_element": "唱名顺序", "value": "先听后摆", "character": "耳朵向导", "motion": "听完整条音列再拖拽", "feedback": f"摆对后还要模唱，才真正服务“{target_stage}”。"},
            ]
        if "三拍子" in target_music_element:
            return [
                {"music_element": "强拍", "value": "第1拍", "character": "领航星", "motion": "先稳稳落点", "feedback": "先找到第一拍，三拍子的摇荡感才会成立。"},
                {"music_element": "弱拍", "value": "第2拍", "character": "摆动月", "motion": "轻轻跟进", "feedback": "第二拍要轻，不要和强拍一样重。"},
                {"music_element": "弱拍", "value": "第3拍", "character": "摆动舟", "motion": "轻轻收回", "feedback": "第三拍继续保持轻拍，形成强弱弱。"},
            ]
        if "附点" in target_music_element:
            return [
                {"music_element": "长音值", "value": "附点部分", "character": "长跳精灵", "motion": "先完成较长弹跳", "feedback": "附点要先稳住较长时值。"},
                {"music_element": "短音值", "value": "后续短音", "character": "短跳精灵", "motion": "再快速接上", "feedback": "后面的短音要紧接出现，不能拖慢。"},
                {"music_element": "长短关系", "value": "先长后短", "character": "节奏桥", "motion": "按顺序通过", "feedback": "听清长短关系，附点节奏才会有弹性。"},
            ]
        if "切分" in target_music_element:
            return [
                {"music_element": "重音转移", "value": "非强拍位置", "character": "夺旗手", "motion": "把旗帜移到新重音", "feedback": "切分不是平均拍，要听到重音转移。"},
                {"music_element": "稳定拍", "value": "底层节拍", "character": "节拍守卫", "motion": "保持原有拍点", "feedback": "底层稳定拍不能丢。"},
                {"music_element": "切分型", "value": "先连后落", "character": "节奏锁", "motion": "完成错位节奏", "feedback": "说出哪里和常规重音不一样。"},
            ]
        if "休止" in target_music_element:
            return [
                {"music_element": "有声拍", "value": "发声", "character": "绿灯音符", "motion": "正常前进", "feedback": "有声处要准确发出。"},
                {"music_element": "无声拍", "value": "停顿", "character": "红灯休止", "motion": "原地停住", "feedback": "休止不是省略，而是有时值的静止。"},
                {"music_element": "节奏完整", "value": "有声+无声", "character": "路口管理员", "motion": "检查整句节奏", "feedback": "完整保留停顿，节奏才会对。"},
            ]
        if "时值" in target_music_element:
            return [
                {"music_element": "长时值", "value": "持续更久", "character": "慢跑员", "motion": "保持更长运动", "feedback": "长时值要稳住，不要抢拍。"},
                {"music_element": "中时值", "value": "两拍左右", "character": "散步员", "motion": "匀速前进", "feedback": "中等时值要保持均匀。"},
                {"music_element": "短时值", "value": "一拍或更短", "character": "跳步员", "motion": "快速通过", "feedback": "短时值要清楚、利落。"},
            ]
        if any(word in target_music_element for word in ["上行", "下行", "旋律", "音高"]):
            return [
                {"music_element": "上行", "value": "音高升高", "character": "攀升鸟", "motion": "往更高处移动", "feedback": "听到音高升高时，路线也要向上。"},
                {"music_element": "下行", "value": "音高降低", "character": "滑降鱼", "motion": "往更低处移动", "feedback": "听到音高降低时，路线要向下。"},
                {"music_element": "保持", "value": "重复音", "character": "停稳星", "motion": "停在同一层", "feedback": "重复音不要误判成上下变化。"},
            ]
        if any(word in target_music_element for word in ["级进", "跳进"]):
            return [
                {"music_element": "级进", "value": "相邻音移动", "character": "一步探险家", "motion": "只走一格", "feedback": "级进是相邻移动，不是跨越。"},
                {"music_element": "跳进", "value": "跨格移动", "character": "跨步探险家", "motion": "跳过中间格", "feedback": "跳进跨度更大，要听出跨越感。"},
                {"music_element": "音程判断", "value": "先听后选", "character": "耳朵向导", "motion": "确认走法", "feedback": "先判断再操作，别只看动画。"},
            ]
        if any(word in target_music_element for word in ["音色", "乐器"]):
            return [
                {"music_element": "音色特征", "value": "先听后选", "character": "音色侦探", "motion": "寻找匹配线索", "feedback": "先抓住声音特点，再选乐器。"},
                {"music_element": "乐器判断", "value": "完成匹配", "character": "证据卡", "motion": "拖到对应对象", "feedback": "说出你为什么这样判断。"},
                {"music_element": "课堂表达", "value": "回到语言描述", "character": "分享话筒", "motion": "完成说明", "feedback": "把听到的依据讲清楚。"},
            ]
        if any(word in target_music_element for word in ["五声", "调式"]):
            return [
                {"music_element": "核心音级", "value": "选择合适音", "character": "调式拼图块", "motion": "放入正确位置", "feedback": "先保证音级符合该调式。"},
                {"music_element": "风格感", "value": "听辨整体气质", "character": "风格罗盘", "motion": "对准相应方向", "feedback": "调式判断要和风格体验连起来。"},
                {"music_element": "短句完整", "value": "形成短乐句", "character": "收束点", "motion": "完成拼接", "feedback": "拼完后要能说出为什么像这个风格。"},
            ]
        if "力度" in target_music_element:
            return [
                {"music_element": "强", "value": "更有力", "character": "浓色刷", "motion": "加深颜色", "feedback": "力度增强时动作和听感都更明显。"},
                {"music_element": "弱", "value": "更轻柔", "character": "淡色刷", "motion": "减轻颜色", "feedback": "力度减弱时不能失去节拍控制。"},
                {"music_element": "变化过程", "value": "渐强或渐弱", "character": "变化轨迹", "motion": "拖出曲线", "feedback": f"这一步是为了服务“{target_objective}”。"},
            ]
        if "速度" in target_music_element:
            return [
                {"music_element": "较快", "value": "加速", "character": "快跑针", "motion": "指向更快区域", "feedback": "速度变化要和音乐形象对应。"},
                {"music_element": "较慢", "value": "减速", "character": "慢行针", "motion": "指向更慢区域", "feedback": "慢不等于散，仍要保持节拍。"},
                {"music_element": "速度判断", "value": "说明理由", "character": "判断卡", "motion": "提交答案", "feedback": f"完成后说出它怎样帮助了“{target_stage}”。"},
            ]
        return [
            {"music_element": target_music_element, "value": "先听后判断", "character": "课堂向导", "motion": "完成第一步判断", "feedback": f"先抓住“{target_music_element}”，不要只看角色表面。"},
            {"music_element": target_music_element, "value": "完成核心操作", "character": "任务精灵", "motion": "拖拽、点击或排序", "feedback": f"这一步要服务“{target_objective}”。"},
            {"music_element": target_music_element, "value": "回到课堂表达", "character": "分享话筒", "motion": "完成说明", "feedback": f"完成后说清楚它为什么适合“{target_stage}”。"},
        ]

    def _music_game_actions_for_lesson_context(self, target_music_element: str, target_stage: str) -> list[str]:
        if any(word in target_music_element for word in ["sol", "mi", "唱名", "高低音", "5音", "3音"]):
            return ["先试听目标音列", "拖拽 sol 和 mi 唱名卡还原顺序", "点击检查挑战并继续闯关", f"最后在“{target_stage}”里把音列模唱出来"]
        if any(word in target_music_element for word in ["拍", "节奏", "时值", "附点", "切分", "休止"]):
            return ["先观察每个角色代表的节奏规则", "拖拽角色组成正确顺序", "点击开始挑战并跟随表现", f"完成后说明这怎样服务“{target_stage}”"]
        if any(word in target_music_element for word in ["旋律", "音高", "上行", "下行", "级进", "跳进"]):
            return ["先听辨音高或旋律变化", "拖拽或选择正确路线", "点击播放验证判断", f"说出这怎样帮助你完成“{target_stage}”任务"]
        if any(word in target_music_element for word in ["音色", "乐器", "调式", "五声", "力度", "速度"]):
            return ["先听或看任务提示", "完成匹配、选择或排序", "查看即时反馈并调整", f"最后把判断带回“{target_stage}”中的课堂表达"]
        return ["理解课堂任务", "完成页面操作挑战", "查看即时反馈", f"用一句话说明这怎样服务“{target_stage}”"]

    @staticmethod
    def _is_pitch_action_response(source: str, target_music_element: str) -> bool:
        pitch_like = any(word in str(target_music_element) for word in ["sol", "mi", "唱名", "高低音", "音高"])
        action_like = any(
            word in str(source)
            for word in ["举手", "举高", "站起", "站立", "蹲下", "手放低", "放低", "身体动作", "肢体动作", "实时响应"]
        )
        return pitch_like and action_like

    @staticmethod
    def _pitch_action_response_actions(target_stage: str) -> list[str]:
        return [
            "先试听 sol-mi 音高关系目标音列",
            "听到 sol 点击高位动作，听到 mi 点击低位动作",
            "根据即时反馈调整动作速度",
            f"最后在“{target_stage}”里边做动作边模唱",
        ]

    def _rules_align_with_target(self, rules: list[dict], target_music_element: str) -> bool:
        if not target_music_element or not isinstance(rules, list):
            return False
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            joined = " ".join(str(rule.get(key, "")) for key in ["music_element", "value", "character", "motion", "feedback"])
            if self._text_targets_lesson(joined, target_music_element, ""):
                return True
        return False

    def _text_targets_lesson(self, text: str, target_music_element: str, target_objective: str) -> bool:
        source = str(text or "").strip()
        if not source:
            return False
        for target in [target_music_element, target_objective]:
            normalized = str(target or "").strip()
            if not normalized:
                continue
            if normalized in source:
                return True
            tokens = [token for token in re.split(r"[，,、；;：:\s（）()]+", normalized) if len(token) >= 2]
            if any(token in source for token in tokens):
                return True
        return False

    def _music_game_for_need(self, need: str, activity_type: str) -> dict:
        game_type = self._infer_music_game_type(need)
        concept = self._infer_music_game_concept(need)
        rules = self._music_game_rules_for_need(need, concept)
        blueprint = build_music_game_blueprint(
            game_type=game_type,
            concept=concept,
            goal=f"让学生通过游戏操作理解“{concept}”，并能用自己的话说出判断依据。",
            source_name=self._music_game_name(game_type, concept),
        )
        game = {
            "enabled": activity_type == "music_game",
            "game_type": game_type,
            "game_family": blueprint["game_family"],
            "activity_fit": blueprint.get("activity_fit", []),
            "preferred_activity": blueprint.get("preferred_activity", ""),
            "source_game_forms": blueprint.get("source_game_forms", []),
            "learning_depth": blueprint.get("learning_depth", []),
            "game_name": blueprint["game_name"],
            "music_concept": concept,
            "goal": blueprint["goal"],
            "mechanic": blueprint["mechanic"],
            "rules": rules,
            "student_actions": self._music_game_actions(game_type),
            "core_loop": blueprint["core_loop"],
            "failure_state": blueprint["failure_state"],
            "progression": blueprint["progression"],
            "target_session_minutes": blueprint["target_session_minutes"],
            "win_condition": "完成正确排序或匹配后点击开始，角色能按音乐规则依次完成挑战，并获得课堂反馈。",
        }
        game["music_logic_contract"] = build_music_logic_contract(need=need, music_game=game)
        return game

    def _infer_music_game_type(self, need: str) -> str:
        explicit_type = infer_game_type_from_text(need)
        if explicit_type != "lesson_mission_game":
            return explicit_type
        if any(word in need for word in ["sol", "mi", "唱名", "高低音", "5音", "3音"]):
            return "sol_mi_pitch_game"
        if any(word in need for word in ["赛跑", "跑过屏幕", "跑道", "动物", "快跑", "慢跑"]):
            return "rhythm_race_game"
        if any(word in need for word in ["节奏拼图", "节奏重建", "时值测试"]):
            return "rhythm_rebuild_challenge"
        if any(word in need for word in ["节奏点按", "节拍闯关", "节奏接龙", "复刻", "跟拍"]):
            return "rhythm_echo_chain"
        if any(word in need for word in ["音阶游戏", "音高定位", "高低选位"]):
            return "pitch_ladder_game"
        if any(word in need for word in ["音符配对", "符号速认", "谱线寻踪", "乐理"]):
            return "notation_match_lab"
        if any(word in need for word in ["片段拼接", "乐段重组", "乐句拼图", "曲式"]):
            return "segment_ordering_studio"
        if any(word in need for word in ["随心编曲", "约束创编", "编曲", "小曲"]):
            return "constrained_composition_lab"
        if any(word in need for word in ["闻声辨器", "音色连连", "曲风匹配", "流派分辨"]):
            return "timbre_evidence_match"
        if any(word in need for word in ["乐章联想", "情绪场景", "场景插画"]):
            return "expression_decision_game"
        if any(word in need for word in ["飞行", "小鸟", "高低", "音高"]):
            return "melody_path_game"
        if any(word in need for word in ["翻牌", "匹配", "找朋友", "消消乐", "卡牌"]):
            return "timbre_detective_game"
        return "lesson_mission_game"

    def _infer_music_game_concept(self, need: str) -> str:
        if any(word in need for word in ["sol", "mi", "唱名", "高低音", "5音", "3音"]):
            return "sol-mi 音高关系"
        if any(word in need for word in ["时值", "全音符", "二分音符", "四分音符", "八分音符"]):
            return "节奏时值"
        if any(word in need for word in ["力度", "渐强", "渐弱", "速度", "情绪", "形象"]):
            return "音乐表现变化"
        if any(word in need for word in ["节奏", "拍", "强弱"]):
            return "节奏与拍点"
        if any(word in need for word in ["音高", "旋律", "上行", "下行"]):
            return "音高走向"
        if any(word in need for word in ["音色", "乐器"]):
            return "乐器音色"
        if any(word in need for word in ["五声", "宫", "商", "角", "徵", "羽", "调式"]):
            return "五声音阶与民族调式"
        if any(word in need for word in ["小组", "接力", "合作", "展示"]):
            return "合作表现"
        return "音乐要素"

    def _music_game_rules_for_need(self, need: str, concept: str) -> list[dict[str, str]]:
        if concept == "sol-mi 音高关系":
            return [
                {"music_element": "sol", "value": "较高的唱名", "character": "小太阳", "motion": "放到较高台阶", "feedback": "听清较高的那个音，再放 sol。"},
                {"music_element": "mi", "value": "较低的唱名", "character": "小叶子", "motion": "放到较低台阶", "feedback": "听清较低的那个音，再放 mi。"},
                {"music_element": "唱名顺序", "value": "完整音列", "character": "音高台阶", "motion": "按顺序排好再检查", "feedback": "摆好后还要模唱，不能只看卡片。"},
            ]
        if concept == "节奏时值":
            whole_character = "慢吞吞的树懒" if "树懒" in need else "慢慢走的乌龟"
            half_character = "散步的大象" if "大象" in need else "稳稳走的小熊"
            quarter_character = "跳跃的兔子" if "兔子" in need else "轻快的小鹿"
            rules = [
                {
                    "music_element": "全音符",
                    "value": "4拍",
                    "character": whole_character,
                    "motion": "用最长时间穿过跑道",
                    "feedback": "听到长音时要稳住四拍。",
                },
                {
                    "music_element": "二分音符",
                    "value": "2拍",
                    "character": half_character,
                    "motion": "用中等速度前进",
                    "feedback": "二分音符保持两拍，不急也不断。",
                },
                {
                    "music_element": "四分音符",
                    "value": "1拍",
                    "character": quarter_character,
                    "motion": "每拍跳一步",
                    "feedback": "四分音符一拍一下，像稳定的脚步。",
                },
            ]
            if "八分" in need:
                rules.append(
                    {
                        "music_element": "八分音符",
                        "value": "半拍",
                        "character": "敏捷的小松鼠",
                        "motion": "半拍冲刺一步",
                        "feedback": "八分音符更短，要听清一拍里的两个小步。",
                    }
                )
            return rules

        if concept == "音高走向":
            return [
                {"music_element": "高音", "value": "向上", "character": "飞高的小鸟", "motion": "飞到更高云朵", "feedback": "音越高，角色越往上。"},
                {"music_element": "低音", "value": "向下", "character": "潜水的小鱼", "motion": "游到更低水层", "feedback": "音越低，角色越往下。"},
                {"music_element": "重复音", "value": "保持", "character": "停稳的星星", "motion": "停在同一高度", "feedback": "重复音保持在同一位置。"},
            ]

        if concept == "乐器音色":
            return [
                {"music_element": "明亮音色", "value": "清脆", "character": "亮色证据卡", "motion": "匹配到明亮乐器", "feedback": "听听声音是不是清亮、穿透。"},
                {"music_element": "柔和音色", "value": "圆润", "character": "柔色证据卡", "motion": "匹配到柔和乐器", "feedback": "柔和音色通常更连贯、圆润。"},
                {"music_element": "打击音色", "value": "短促", "character": "节奏证据卡", "motion": "匹配到打击乐器", "feedback": "短促、有颗粒感的声音常常来自打击乐。"},
            ]

        if concept == "五声音阶与民族调式":
            return [
                {"music_element": "宫", "value": "稳定起点", "character": "宫格起点", "motion": "放在乐句开头或收束处", "feedback": "宫音能带来稳定感。"},
                {"music_element": "商角徵羽", "value": "五声音级", "character": "五声拼图块", "motion": "拼成短乐句", "feedback": "只能使用五声音级，听听民族风格是否明显。"},
                {"music_element": "短句收束", "value": "完整乐句", "character": "收束铃", "motion": "完成最后一格", "feedback": "拼完后要能说出为什么像这个风格。"},
            ]

        if concept == "音乐表现变化":
            return [
                {"music_element": "力度", "value": "强弱变化", "character": "力度滑块", "motion": "推向更强或更弱", "feedback": "力度选择要和音乐情绪相符。"},
                {"music_element": "速度", "value": "快慢变化", "character": "速度指针", "motion": "指向合适档位", "feedback": "速度变化要保持节拍感。"},
                {"music_element": "情绪形象", "value": "说明理由", "character": "表情卡", "motion": "提交判断", "feedback": "把你听到的变化讲出来。"},
            ]

        if concept == "合作表现":
            return [
                {"music_element": "第一组任务", "value": "接力开始", "character": "起点任务卡", "motion": "完成第一段表现", "feedback": "第一组要给后面小组留下清楚节拍。"},
                {"music_element": "下一组任务", "value": "接上前组", "character": "接力任务卡", "motion": "延续或回应前一组", "feedback": "接力重点是衔接，不是各玩各的。"},
                {"music_element": "全班展示", "value": "合并完成", "character": "展示徽章", "motion": "共同完成展示", "feedback": "最后说出合作中听到的音乐变化。"},
            ]

        return [
            {"music_element": concept, "value": "规则一", "character": "小小指挥家", "motion": "根据音乐提示行动", "feedback": "做出选择后说出音乐理由。"},
            {"music_element": concept, "value": "规则二", "character": "节拍伙伴", "motion": "跟随节拍完成动作", "feedback": "如果不确定，可以重新听一次再挑战。"},
            {"music_element": concept, "value": "规则三", "character": "旋律精灵", "motion": "完成最后展示", "feedback": "把你的判断讲给同伴听。"},
        ]

    def _music_game_name(self, game_type: str, concept: str) -> str:
        form = game_form_for_type(game_type)
        if game_type in {
            "sol_mi_pitch_game",
            "melody_path_game",
            "timbre_detective_game",
            "pentatonic_grid_game",
            "group_relay_game",
            "expression_control_game",
            "lesson_mission_game",
        }:
            return form["label"]
        return {
            "rhythm_race_game": f"{concept}赛跑",
            "sol_mi_pitch_game": "sol-mi 音高台阶",
            "custom_music_game": f"{concept}小游戏",
        }.get(game_type, f"{concept}小游戏")

    def _music_game_actions(self, game_type: str) -> list[str]:
        game_type = canonical_game_type(game_type)
        if game_type in {
            "sol_mi_pitch_game",
            "melody_path_game",
            "timbre_detective_game",
            "pentatonic_grid_game",
            "group_relay_game",
            "expression_control_game",
            "lesson_mission_game",
        }:
            return list(game_form_for_type(game_type)["student_actions"])
        if game_type == "rhythm_race_game":
            return ["观察角色和对应时值", "拖拽角色组成节奏句子", "点击开始赛跑", "根据反馈调整顺序并再次挑战"]
        return ["理解游戏规则", "完成拖拽或点击操作", "查看即时反馈", "重新挑战并完成课堂分享"]

    def _infer_mood(self, need: str, fallback: str) -> str:
        for mood in ["明亮", "抒情", "忧伤", "活泼", "庄重", "神秘", "民族风", "富有张力"]:
            if mood in need:
                return mood
        return fallback

    def _infer_theme_or_song(self, need: str, fallback: str) -> str:
        song = self._infer_song_name(need)
        return song if song != "自选歌曲" else fallback

    def _build_title(self, need: str, activity_type: str) -> str:
        label = {
            "listening": "体验性聆听活动网页",
            "performance": "表现性闯关活动网页",
            "creation": "创造性音乐拼图网页",
            "music_game": "音乐小游戏网页",
            "mixed": "综合音乐课堂活动网页",
        }[activity_type]
        return label if len(need) > 6 else f"{need}{label}"

    def _build_subtitle(self, activity_type: str) -> str:
        return {
            "listening": "聚焦聆听体验：上传音频后调节音乐要素，学生完成对比聆听。",
            "performance": "聚焦表现训练：学生按关卡逐级练习、解锁、展示。",
            "creation": "聚焦创意活动：学生使用素材卡片完成旋律、节奏或风格创作。",
            "music_game": "聚焦音乐小游戏：学生通过角色、规则和反馈理解音乐概念。",
            "mixed": "按体验、表现、创造三维活动组织的综合音乐课堂工具。",
        }[activity_type]

    def _template_for_activity(self, activity_type: str) -> str:
        return template_id_for_activity(activity_type)

    def _technical_strategy(self, activity_type: str) -> dict:
        return technical_strategy_for_activity(activity_type)

    def _teacher_notes_for_activity(self, activity_type: str) -> list[str]:
        notes = {
            "listening": [
                "先让学生听原始片段，再切换一个音乐要素进行对比。",
                "每次只改变一个要素，帮助学生说清楚听到的变化。",
                "最后让学生用自己的话总结调式、节奏、速度或音色带来的感受差异。",
            ],
            "performance": [
                "每一关只聚焦一个可观察的表现目标，避免一次评价过多内容。",
                "先个人尝试，再同伴互评，最后小组展示。",
                "通关标准要让学生一眼看懂，可以用勾选、徽章或得分反馈建立信心。",
            ],
            "creation": [
                "先限制素材数量，再逐步开放更多选择，降低创作门槛。",
                "鼓励学生解释为什么这样排列音高、节奏或结构功能。",
                "展示时同时评价统一性、变化性和情绪表达。",
            ],
            "music_game": [
                "先让学生说出每个角色对应的音乐规则，再开始操作。",
                "游戏反馈要服务音乐理解，不只追求输赢。",
                "完成后请学生用一句话说明：我为什么这样排列或选择。",
            ],
            "mixed": [
                "先聆听建立要素经验，再通过表现巩固，最后迁移到创作。",
                "表现和创造环节不依赖 MIDI 分析，确保课堂运行更轻便。",
                "如果时间有限，可只保留一个聆听对比和一个最终展示任务。",
            ],
        }
        return notes[activity_type]

    def _interaction_model_for_activity(self, need: str, activity_type: str) -> dict:
        if activity_type == "performance":
            primary = self._infer_performance_interaction(need)
            return {
                "primary": primary,
                "components": self._components_for_interaction(primary),
                "student_actions": [
                    "选择当前关卡",
                    "点击开始挑战",
                    "根据提示完成演唱、敲击、律动或听辨任务",
                    "查看即时反馈并继续下一关",
                ],
                "teacher_controls": ["重置进度", "调整通关标准", "手动确认通关", "展示全班任务说明"],
                "artifact_outputs": ["关卡地图", "通关徽章", "课堂反馈语", "最终展示任务"],
            }
        if activity_type == "creation":
            primary = self._infer_creation_interaction(need)
            return {
                "primary": primary,
                "components": self._components_for_interaction(primary),
                "student_actions": [
                    "选择调性和音色",
                    "拖拽素材或绘制旋律线",
                    "切换声部并试听",
                    "保存或重置自己的创作",
                ],
                "teacher_controls": ["限制小节数", "指定调式", "提供示范素材", "展示学生作品"],
                "artifact_outputs": ["音乐素材拼图", "双声部旋律草稿", "可试听作品", "创作说明"],
            }
        if activity_type == "listening":
            return {
                "primary": "element_transform_lab",
                "components": ["audio_upload", "element_control_panel", "compare_player", "listening_prompt_cards"],
                "student_actions": ["上传或选择音频", "调节一个音乐要素", "对比试听", "记录听辨发现"],
                "teacher_controls": ["限定对比要素", "重置参数", "引导学生描述变化"],
                "artifact_outputs": ["原始版本", "改编版本", "听辨问题", "课堂总结"],
            }
        if activity_type == "music_game":
            primary = self._infer_music_game_type(need)
            return {
                "primary": primary,
                "components": self._components_for_interaction(primary),
                "student_actions": self._music_game_actions(primary),
                "teacher_controls": ["调整角色数量", "重置挑战", "展示规则说明", "组织学生说出音乐理由"],
                "artifact_outputs": ["游戏规则卡", "可操作游戏区", "即时反馈", "课堂分享提示"],
            }
        return {
            "primary": "three_phase_music_studio",
            "components": [
                "listening_lab",
                "level_map",
                "creation_board",
                "reflection_panel",
            ],
            "student_actions": ["先听辨", "再闯关表现", "最后创作展示", "完成课堂反思"],
            "teacher_controls": ["选择活动阶段", "调整任务难度", "重置课堂进度", "组织小组展示"],
            "artifact_outputs": ["聆听对比", "表现成绩", "创作作品", "课堂评价"],
        }

    def _scoring_for_activity(self, need: str, activity_type: str) -> dict:
        if activity_type == "performance":
            timing_weight = 0.35 if any(word in need for word in ["节奏", "敲击", "跟随", "拍"]) else 0.2
            return {
                "enabled": True,
                "pass_score": 80,
                "feedback_mode": "real_time_and_summary",
                "metrics": [
                    {
                        "id": "accuracy",
                        "label": "任务准确度",
                        "weight": 0.4,
                        "feedback": "是否完成本关指定的音乐任务。",
                    },
                    {
                        "id": "timing",
                        "label": "节奏稳定度",
                        "weight": timing_weight,
                        "feedback": "是否能跟随拍点或音乐保持稳定。",
                    },
                    {
                        "id": "expression",
                        "label": "表现表达",
                        "weight": round(0.6 - timing_weight, 2),
                        "feedback": "是否能用声音、动作或乐器表现音乐特点。",
                    },
                ],
            }
        if activity_type == "creation":
            return {
                "enabled": True,
                "pass_score": 70,
                "feedback_mode": "rubric_cards",
                "metrics": [
                    {"id": "coherence", "label": "乐句连贯", "weight": 0.35, "feedback": "作品是否有开始、发展和收束。"},
                    {"id": "material_use", "label": "素材运用", "weight": 0.3, "feedback": "是否合理使用指定音高、节奏或调式素材。"},
                    {"id": "creativity", "label": "创意表达", "weight": 0.35, "feedback": "是否能说明自己的音乐想法。"},
                ],
            }
        if activity_type == "listening":
            return {
                "enabled": True,
                "pass_score": 0,
                "feedback_mode": "guided_reflection",
                "metrics": [
                    {"id": "contrast", "label": "听辨差异", "weight": 0.45, "feedback": "能否说出两个版本的音乐要素变化。"},
                    {"id": "vocabulary", "label": "音乐描述", "weight": 0.25, "feedback": "能否使用合适的音乐词汇描述感受。"},
                    {"id": "reasoning", "label": "判断依据", "weight": 0.3, "feedback": "能否说明为什么听起来不同。"},
                ],
            }
        if activity_type == "music_game":
            return {
                "enabled": True,
                "pass_score": 80,
                "feedback_mode": "playful_real_time",
                "metrics": [
                    {"id": "rule_match", "label": "规则对应", "weight": 0.45, "feedback": "音乐概念和角色动作是否匹配。"},
                    {"id": "sequence", "label": "操作顺序", "weight": 0.3, "feedback": "是否能按要求排列、匹配或完成路线。"},
                    {"id": "explain", "label": "音乐说明", "weight": 0.25, "feedback": "能否说出自己的音乐判断理由。"},
                ],
            }
        return {
            "enabled": True,
            "pass_score": 75,
            "feedback_mode": "phase_summary",
            "metrics": [
                {"id": "listening", "label": "聆听发现", "weight": 0.3, "feedback": "能否听出音乐要素变化。"},
                {"id": "performance", "label": "表现完成", "weight": 0.35, "feedback": "能否完成表现任务。"},
                {"id": "creation", "label": "创作表达", "weight": 0.35, "feedback": "能否完成并解释创作。"},
            ],
        }

    def _runtime_behaviors_for_activity(self, need: str, activity_type: str) -> dict:
        requires_audio = activity_type == "listening" or any(word in need for word in ["上传音频", "跟随音乐", "播放音乐"])
        return {
            "save_progress": activity_type in {"performance", "music_game", "mixed"},
            "unlock_next_step": activity_type in {"performance", "mixed"},
            "countdown": activity_type in {"performance", "music_game"} or any(word in need for word in ["倒计时", "跟随", "闯关", "赛跑"]),
            "auto_play_after_start": activity_type == "music_game" or any(word in need for word in ["跟随音乐", "自动播放", "倒计时"]),
            "resettable": True,
            "allow_teacher_override": activity_type in {"performance", "music_game", "mixed"},
            "allow_continue_revision": True,
            "requires_audio_upload": requires_audio,
            "playback": "sampled_soundfont_first" if activity_type in {"creation", "music_game", "mixed"} else "audio_compare_with_sampled_soundfont_preview" if activity_type == "listening" else "sampled_soundfont_prompt_sound",
        }

    def _blueprint_plan_for_need(self, need: str, activity_type: str) -> dict:
        blueprint_id = self._template_for_activity(activity_type)
        blueprint_label = technical_strategy_for_activity(activity_type).get("blueprint_label", blueprint_id)
        interaction_primary = self._interaction_model_for_activity(need, activity_type).get("primary", "")
        components = self._components_for_interaction(interaction_primary)
        if activity_type == "music_game":
            game_type = canonical_game_type(self._infer_music_game_type(need))
            form = game_form_for_type(game_type)
            matched_template = detect_template_match_from_text(need)
            if matched_template:
                selection_reason = f"需求中显式命中了现成音乐游戏模板，因此优先使用 {matched_template} 承载课堂操作。"
                current_blueprint_id = matched_template
                current_blueprint_label = "已匹配音乐游戏模板"
            else:
                selection_reason = "需求没有显式命中内置模板，应保留玩法语义并交给 OpenCode 自由生成页面。"
                current_blueprint_id = "OpenEnded_MusicGame"
                current_blueprint_label = "自由生成音乐游戏"
            return {
                "blueprint_id": current_blueprint_id,
                "blueprint_label": current_blueprint_label,
                "selection_reason": selection_reason,
                "primary_interaction": form["primary"],
                "gameplay_focus": form["mechanic"],
                "progression_strategy": "先给出可理解的任务入口，再通过多轮挑战、生命值或星级推进难度。",
                "component_focus": list(form["components"]),
            }
        reason_map = {
            "listening": f"需求强调对比聆听与音乐要素调节，因此优先使用{blueprint_label}。",
            "performance": f"需求强调关卡表现与课堂挑战流程，因此优先使用{blueprint_label}。",
            "creation": f"需求强调学生动手创编与试听，因此优先使用{blueprint_label}。",
            "mixed": f"需求跨多个课堂阶段，因此先以{blueprint_label}组织，再按主任务收束为单一主操作区。",
        }
        focus_map = {
            "listening": "先上传或选择材料，再围绕单个音乐要素做对比聆听与表达。",
            "performance": "先明确当前关任务，再开始挑战、获得反馈并解锁下一关。",
            "creation": "先选择素材或声部，再操作创编、试听修正并展示结果。",
            "mixed": "按课堂阶段组织，但每个阶段都必须保留真实操作和结果反馈。",
        }
        progression_map = {
            "listening": "先做单要素变化，再做对比描述，最后回到课堂讨论。",
            "performance": "按由易到难的关卡推进，始终保持开始挑战、反馈、重试闭环。",
            "creation": "先提供低门槛示范，再开放修改，最后让学生形成完整作品。",
            "mixed": "从感知进入任务，再进入表现或创编，最后回到展示与反思。",
        }
        return {
            "blueprint_id": blueprint_id,
            "blueprint_label": blueprint_label,
            "selection_reason": reason_map.get(activity_type, f"当前需求优先使用{blueprint_label}。"),
            "primary_interaction": interaction_primary,
            "gameplay_focus": focus_map.get(activity_type, "围绕课堂目标组织真实操作。"),
            "progression_strategy": progression_map.get(activity_type, "保持可操作闭环并逐步升级任务。"),
            "component_focus": components,
        }

    def _generation_strategy_for_need(self, need: str, activity_type: str) -> dict:
        music_game_template_match = detect_template_match_from_text(need) if activity_type == "music_game" else ""
        render_priority = {
            "listening": ["先完成上传与控件", "再完成对比试听", "最后补课堂反馈"],
            "performance": ["先完成开始挑战与关卡流程", "再完成即时反馈", "最后补展示与总结"],
            "creation": ["先完成创作操作区", "再完成试听与声部控制", "最后补说明与展示"],
            "music_game": ["先完成可玩主循环", "再完成关卡进度或生命值", "最后补反馈与反思"],
            "mixed": ["先确定单一主活动", "再完成主交互", "最后补阶段切换与课堂收束"],
        }.get(activity_type, ["先完成主操作区", "再完成反馈", "最后补展示"])
        goal_map = {
            "listening": "生成可直接用于课堂对比聆听的交互网页，而不是静态说明页。",
            "performance": "生成真正能闯关、能反馈、能重试的课堂表现页，而不是规则文本页。",
            "creation": "生成真正能拖拽、绘制、试听、切换声部的创作页，而不是创意说明页。",
            "music_game": "生成真正可玩的音乐小游戏，而不是把规则写进网页。",
            "mixed": "生成以单一主活动为核心的课堂页，而不是把所有模块平铺堆叠。",
        }
        if activity_type == "music_game" and not music_game_template_match:
            return {
                "mode": "freeform_music_game",
                "artifact_goal": "生成真正可玩的原创音乐小游戏网页；保留玩法语义，但不要强制套任何内置模板。",
                "opencode_execution_target": "围绕用户需求、歌曲材料和音乐逻辑契约直接生成网页游戏，不先套模板骨架。",
                "prefer_incremental_revision": False,
                "render_priority": render_priority,
            }
        return {
            "mode": "blueprint_first_then_opencode",
            "artifact_goal": goal_map.get(activity_type, "生成真实可操作的课堂网页。"),
            "opencode_execution_target": "在选定活动母版基础上完成增量式页面生成与改写。",
            "prefer_incremental_revision": True,
            "render_priority": render_priority,
        }

    def _prompt_contract_for_need(self, need: str, activity_type: str) -> dict:
        source = re.sub(r"\s+", " ", str(need or "")).strip()
        must_include = self._extract_must_include_terms(source)
        must_not_include = self._unrequested_feature_terms(source, activity_type)
        scope = {
            "listening": "只实现聆听上传、要素调节、对比试听和反馈。",
            "performance": "只实现表现闯关、开始挑战、反馈、重试和通关。",
            "creation": "只实现用户要求的创作方式、试听、重置和反馈。",
            "music_game": "只实现用户要求的音乐小游戏玩法、角色、操作、反馈和胜利条件。",
            "mixed": "只实现用户要求的课堂活动组合，不额外堆叠无关模块。",
        }.get(activity_type, "只实现用户要求的课堂网页功能。")
        return {
            "original_user_need": source,
            "must_include": must_include,
            "must_not_include": must_not_include,
            "exact_user_constraints": must_include[:12],
            "allowed_feature_scope": scope,
            "avoid_unrequested_features": True,
        }

    def _coerce_prompt_contract(self, spec: dict, *, need: str = "") -> dict:
        activity_type = str(spec.get("activity_type") or "mixed")
        generated = self._prompt_contract_for_need(need or str(spec.get("original_user_need", "")), activity_type)
        provided = spec.get("user_prompt_contract") if isinstance(spec.get("user_prompt_contract"), dict) else {}
        original = str(provided.get("original_user_need") or spec.get("original_user_need") or generated["original_user_need"])
        must_include = _merge_unique_strings(
            _string_list(provided.get("must_include"), []),
            generated["must_include"],
        )
        must_not_include = _merge_unique_strings(
            _string_list(provided.get("must_not_include"), []),
            generated["must_not_include"],
        )
        return {
            "original_user_need": original,
            "must_include": must_include[:18],
            "must_not_include": must_not_include[:18],
            "exact_user_constraints": _merge_unique_strings(
                _string_list(provided.get("exact_user_constraints"), []),
                generated["exact_user_constraints"],
            )[:12],
            "allowed_feature_scope": str(provided.get("allowed_feature_scope") or generated["allowed_feature_scope"]),
            "avoid_unrequested_features": bool(provided.get("avoid_unrequested_features", True)),
        }

    def _extract_must_include_terms(self, need: str) -> list[str]:
        terms: list[str] = []
        for quoted in re.findall(r"《([^》]{1,40})》|“([^”]{1,40})”|\"([^\"]{1,40})\"", need):
            terms.extend(part.strip() for part in quoted if part and part.strip())
        keyword_groups = [
            "小学",
            "初中",
            "高中",
            "一年级",
            "二年级",
            "三年级",
            "四年级",
            "五年级",
            "六年级",
            "节奏",
            "时值",
            "全音符",
            "二分音符",
            "四分音符",
            "八分音符",
            "附点",
            "切分",
            "休止",
            "音高",
            "旋律",
            "sol",
            "mi",
            "do",
            "re",
            "宫",
            "商",
            "角",
            "徵",
            "羽",
            "五声",
            "拖拽",
            "点击",
            "排列",
            "匹配",
            "赛跑",
            "跑过屏幕",
            "动物",
            "树懒",
            "大象",
            "兔子",
            "角色",
            "拼图",
            "网格",
            "旋律线",
            "双声部",
            "调性",
            "音色",
            "钢琴",
            "关卡",
            "星级",
            "生命值",
            "倒计时",
            "全音符=4拍",
            "二分音符=2拍",
            "四分音符=1拍",
        ]
        for keyword in keyword_groups:
            if keyword in need:
                terms.append(keyword)
        for match in re.findall(r"([一二三四五六七八九十0-9]+)\s*[个道]?关", need):
            terms.append(f"{match}关")
        for left, right in re.findall(r"([\u4e00-\u9fa5A-Za-z0-9/]+)\s*[=＝]\s*([\u4e00-\u9fa5A-Za-z0-9/]+)", need):
            terms.append(left)
            terms.append(right)
            terms.append(f"{left}={right}")
        return _merge_unique_strings(terms, [])

    def _unrequested_feature_terms(self, need: str, activity_type: str) -> list[str]:
        candidates = {
            "排行榜": ["排行榜", "排行"],
            "登录": ["登录", "账号", "用户中心"],
            "录音": ["录音", "麦克风"],
            "上传音频": ["上传音频", "上传"],
            "双声部": ["双声部", "声部"],
            "网格": ["网格", "旋律线"],
            "示范旋律": ["示范", "示范旋律"],
            "教师面板": ["教师面板", "教师控制台"],
            "复杂评分": ["评分维度", "评价量表"],
        }
        blocked = []
        for feature, tokens in candidates.items():
            if not any(token in need for token in tokens):
                blocked.append(feature)
        if activity_type == "listening":
            blocked = [item for item in blocked if item not in {"上传音频"}]
        if activity_type == "creation":
            # 创造工具默认应有网格旋律线，不应禁止
            blocked = [item for item in blocked if item not in {"网格", "双声部"}]
        return blocked

    def _visual_theme_for_need(self, need: str, activity_type: str) -> dict:
        theme_options = [
            ("magic_forest", ["森林", "魔法", "山魔"], "魔幻森林", ["#142716", "#314f38", "#f0b84f", "#d87583"]),
            ("stage_spotlight", ["舞台", "表演", "演出"], "舞台聚光", ["#1b1734", "#ffcf70", "#e55d87", "#6dd6ff"]),
            ("ink_chinese", ["国风", "中国", "古诗", "五声", "古筝"], "水墨国风", ["#f7efe1", "#22352a", "#b78645", "#7b9c87"]),
            ("ocean_rhythm", ["海洋", "水", "波浪"], "海洋律动", ["#e8fbff", "#0f5f78", "#35b6c8", "#f3c969"]),
            ("music_lab", ["实验", "探索", "调式", "音色"], "音乐实验室", ["#f7f3e8", "#25324d", "#25a99b", "#f2b84b"]),
            ("playground_race", ["游戏", "小游戏", "赛跑", "动物", "跑道"], "节奏游乐场", ["#fff2d8", "#1f3b4d", "#f5a623", "#5fc7a1"]),
        ]
        selected = ("warm_classroom", "温暖课堂", ["#fff8df", "#26324f", "#ffd45f", "#ff8f6a"])
        for key, keywords, name, palette in theme_options:
            if any(keyword in need for keyword in keywords):
                selected = (key, name, palette)
                break

        layout = {
            "performance": "level_map_with_challenge_panel",
            "creation": "split_workspace_with_preview",
            "listening": "control_lab_with_compare_player",
            "music_game": "playground_game_board",
            "mixed": "three_phase_dashboard",
        }[activity_type]
        return {
            "name": selected[1],
            "mood": "活泼" if "小学" in need or activity_type in {"performance", "creation", "music_game"} else "清晰",
            "layout": layout,
            "palette": selected[2],
            "illustration_style": "小插图、徽章和音乐符号点缀",
            "motion": "进入时轻微浮动，通关或完成时有明确庆祝动效",
        }

    def _coerce_interaction_model(self, spec: dict) -> dict:
        generated = self._interaction_model_for_activity(spec.get("title", "") + spec.get("subtitle", ""), spec["activity_type"])
        blueprint_plan = spec.get("blueprint_plan") if isinstance(spec.get("blueprint_plan"), dict) else {}
        if blueprint_plan.get("primary_interaction"):
            generated["primary"] = str(blueprint_plan["primary_interaction"])
            generated["components"] = self._components_for_interaction(generated["primary"])
        if spec["activity_type"] == "music_game" and isinstance(spec.get("music_game"), dict):
            primary = canonical_game_type(str(spec["music_game"].get("game_type", "")))
            generated["primary"] = primary
            generated["components"] = self._components_for_interaction(primary)
            generated["student_actions"] = _string_list(spec["music_game"].get("student_actions"), generated["student_actions"])
        provided = spec.get("interaction_model") if isinstance(spec.get("interaction_model"), dict) else {}
        return {
            "primary": str(provided.get("primary") or generated["primary"]),
            "components": normalize_component_ids(_string_list(provided.get("components"), generated["components"])),
            "student_actions": _string_list(provided.get("student_actions"), generated["student_actions"]),
            "teacher_controls": _string_list(provided.get("teacher_controls"), generated["teacher_controls"]),
            "artifact_outputs": _string_list(provided.get("artifact_outputs"), generated["artifact_outputs"]),
        }

    def _coerce_scoring(self, spec: dict) -> dict:
        generated = self._scoring_for_activity(spec.get("title", "") + spec.get("subtitle", ""), spec["activity_type"])
        provided = spec.get("scoring") if isinstance(spec.get("scoring"), dict) else {}
        metrics = provided.get("metrics") if isinstance(provided.get("metrics"), list) else generated["metrics"]
        clean_metrics = []
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            clean_metrics.append(
                {
                    "id": str(metric.get("id") or "metric"),
                    "label": str(metric.get("label") or "评价维度"),
                    "weight": float(metric.get("weight", 0)),
                    "feedback": str(metric.get("feedback") or "根据课堂表现给予反馈。"),
                }
            )
        return {
            "enabled": bool(provided.get("enabled", generated["enabled"])),
            "pass_score": int(provided.get("pass_score", generated["pass_score"])),
            "feedback_mode": str(provided.get("feedback_mode") or generated["feedback_mode"]),
            "metrics": clean_metrics or generated["metrics"],
        }

    def _coerce_runtime_behaviors(self, spec: dict) -> dict:
        generated = self._runtime_behaviors_for_activity(spec.get("title", "") + spec.get("subtitle", ""), spec["activity_type"])
        provided = spec.get("runtime_behaviors") if isinstance(spec.get("runtime_behaviors"), dict) else {}
        return {
            "save_progress": bool(provided.get("save_progress", generated["save_progress"])),
            "unlock_next_step": bool(provided.get("unlock_next_step", generated["unlock_next_step"])),
            "countdown": bool(provided.get("countdown", generated["countdown"])),
            "auto_play_after_start": bool(provided.get("auto_play_after_start", generated["auto_play_after_start"])),
            "resettable": bool(provided.get("resettable", generated["resettable"])),
            "allow_teacher_override": bool(provided.get("allow_teacher_override", generated["allow_teacher_override"])),
            "allow_continue_revision": bool(provided.get("allow_continue_revision", generated["allow_continue_revision"])),
            "requires_audio_upload": bool(provided.get("requires_audio_upload", generated["requires_audio_upload"])),
            "playback": str(provided.get("playback") or generated["playback"]),
        }

    def _coerce_visual_theme(self, spec: dict) -> dict:
        generated = self._visual_theme_for_need(spec.get("title", "") + spec.get("subtitle", ""), spec["activity_type"])
        provided = spec.get("visual_theme") if isinstance(spec.get("visual_theme"), dict) else {}
        return {
            "name": str(provided.get("name") or generated["name"]),
            "mood": str(provided.get("mood") or generated["mood"]),
            "layout": str(provided.get("layout") or generated["layout"]),
            "palette": _string_list(provided.get("palette"), generated["palette"]),
            "illustration_style": str(provided.get("illustration_style") or generated["illustration_style"]),
            "motion": str(provided.get("motion") or generated["motion"]),
        }

    def _coerce_blueprint_plan(self, spec: dict, *, need: str = "") -> dict:
        source_need = need or " ".join(
            [
                str(spec.get("title", "")),
                str(spec.get("subtitle", "")),
                str(spec.get("song_name", "")),
                str(spec.get("target_music_element", "")),
            ]
        )
        generated = self._blueprint_plan_for_need(source_need, spec["activity_type"])
        provided = spec.get("blueprint_plan") if isinstance(spec.get("blueprint_plan"), dict) else {}
        component_focus = normalize_component_ids(
            _string_list(provided.get("component_focus"), generated["component_focus"])
        )
        if not component_focus:
            component_focus = generated["component_focus"]
        return {
            "blueprint_id": str(provided.get("blueprint_id") or spec.get("blueprint_id") or generated["blueprint_id"]),
            "blueprint_label": str(provided.get("blueprint_label") or generated["blueprint_label"]),
            "selection_reason": str(provided.get("selection_reason") or generated["selection_reason"]),
            "primary_interaction": str(provided.get("primary_interaction") or generated["primary_interaction"]),
            "gameplay_focus": str(provided.get("gameplay_focus") or generated["gameplay_focus"]),
            "progression_strategy": str(provided.get("progression_strategy") or generated["progression_strategy"]),
            "component_focus": component_focus,
        }

    def _coerce_generation_strategy(self, spec: dict, *, need: str = "") -> dict:
        source_need = need or " ".join(
            [
                str(spec.get("title", "")),
                str(spec.get("subtitle", "")),
                str(spec.get("song_name", "")),
            ]
        )
        generated = self._generation_strategy_for_need(source_need, spec["activity_type"])
        provided = spec.get("generation_strategy") if isinstance(spec.get("generation_strategy"), dict) else {}
        return {
            "mode": str(provided.get("mode") or generated["mode"]),
            "artifact_goal": str(provided.get("artifact_goal") or generated["artifact_goal"]),
            "opencode_execution_target": str(
                provided.get("opencode_execution_target") or generated["opencode_execution_target"]
            ),
            "prefer_incremental_revision": bool(
                provided.get("prefer_incremental_revision", generated["prefer_incremental_revision"])
            ),
            "render_priority": _string_list(provided.get("render_priority"), generated["render_priority"]),
        }

    def _infer_performance_interaction(self, need: str) -> str:
        if any(word in need for word in ["节奏", "敲击", "拍点", "打击"]):
            return "rhythm_tap_challenge"
        if any(word in need for word in ["听辨", "辨认", "选择"]):
            return "listening_quiz_challenge"
        if any(word in need for word in ["律动", "身体", "动作"]):
            return "body_percussion_challenge"
        if any(word in need for word in ["演唱", "接唱", "模唱"]):
            return "call_response_singing"
        return "level_map_challenge"

    def _infer_creation_interaction(self, need: str) -> str:
        if any(word in need for word in ["双声部", "两条线", "声部"]):
            return "two_voice_melody_grid"
        if any(word in need for word in ["网格", "旋律线", "画旋律"]):
            return "melody_grid_composer"
        if any(word in need for word in ["续写", "接龙"]):
            return "melody_continuation_board"
        if any(word in need for word in ["填空", "补空"]):
            return "note_fill_blank_puzzle"
        return "drag_drop_music_puzzle"

    def _components_for_interaction(self, interaction: str) -> list[str]:
        return components_for_interaction(interaction)

    def _infer_creation_mode(self, need: str) -> str:
        if any(word in need for word in ["网格", "旋律线", "画旋律"]):
            return "melody_grid"
        if any(word in need for word in ["填空", "补空", "补位"]):
            return "note_fill_blank"
        if any(word in need for word in ["续写", "接龙"]):
            return "melody_continuation"
        if any(word in need for word in ["重组", "风格"]):
            return "style_remix"
        if any(word in need for word in ["节奏", "拼图"]):
            return "rhythm_puzzle"
        return "free_assembly"

    @staticmethod
    def _openai_http_client() -> httpx.Client:
        # 服务端调用模型时不继承本机代理，避免桌面代理把请求拖死。
        return httpx.Client(trust_env=False)


def _inspiration_template_context() -> str:
    lines: list[str] = []
    for template in list_game_templates():
        template_id = str(template.get("template_id") or "")
        label = INSPIRATION_TEMPLATE_LABELS.get(template_id, str(template.get("label") or template_id))
        targets = "、".join(str(item) for item in template.get("learning_targets", [])[:5] if str(item).strip())
        actions = "、".join(str(item) for item in template.get("student_actions", [])[:5] if str(item).strip())
        description = str(template.get("description") or "").strip()
        lines.append(f"- {label}：适用要素 {targets or '见模板配置'}；学生动作 {actions or '见模板配置'}；边界 {description}")
    return "\n".join(lines)


def _inspiration_request_grounding_context(message: str) -> str:
    template_id = _matched_production_template_id(message)
    if template_id:
        label = INSPIRATION_TEMPLATE_LABELS.get(template_id, template_id)
        reason = INSPIRATION_TEMPLATE_REASONS.get(template_id, "它是当前生产模板库中最贴近这个需求的模板。")
        need = INSPIRATION_TEMPLATE_NEED_HINTS.get(template_id, _compact_inspiration_need(message))
        return "\n".join(
            [
                "本轮必须依据生产模板库回答，但可以像正常顾问一样先交流、追问和解释。",
                f"命中模板 ID：{template_id}",
                f"命中模板名：{label}",
                f"适配理由：{reason}",
                f"如果用户想直接生成，可参考这句生成框文案：{need}",
                "不要每次都使用固定标题。可以自然提到模板方向；信息不足时优先追问年级、曲目、音乐要素或学生动作。",
            ]
        )
    return "\n".join(
        [
            "本轮必须依据生产模板库回答，但要像正常顾问一样交流。",
            "当前用户需求未命中成熟内置模板。",
            "不要发散或编造新模板；如果谈到具体游戏玩法，说明暂无成熟内置模板，并温和建议改写到现有生产模板方向。",
        ]
    )


CHAT_SYSTEM_PROMPT = f"""
你是"灵感助手"，一个面向中小学音乐教师的对话顾问。
你的回答要简短、温暖、具体，使用中文。
你不是页面生成器、不是代码生成器、也不是 OpenCode 执行层。
你只能做以下事情：
1. 给教学灵感、课堂活动设计建议、音乐游戏创意。
2. 润色和优化教师的需求描述。
3. 回答音乐教学相关问题，提供课堂实施建议。
4. 解释已生成工具的使用方法。
你绝对不能：
- 输出 HTML、CSS、JavaScript 代码或任何网页代码。
- 输出 MIDI、Python 或其他技术代码。
- 输出 Markdown 代码块、伪代码、文件结构、命令行或可复制到工程里的实现片段。
- 说"正在生成网页"或"正在编写代码"。
- 承诺自己已经生成、正在生成或将直接生成代码/网页产物。
- 展示后台技术路线、命令、模型或实现细节。
如果用户要求生成工具、网页或代码，请温和地拒绝直接生成，并改为输出“可放入生成框的需求描述”和 2-3 条玩法建议。

模板优先边界：
- 当你给出具体音乐游戏玩法建议时，必须先匹配以下内置模板，不能编造未注册模板或暗示系统能生成未覆盖模板。
- 如果命中模板，可以自然说明更接近哪个模板方向和原因；不要每次都套用固定三段式。
- 如果信息不足，先正常交流并追问年级、曲目、音乐要素、学生动作或通关表达。
- 如果没有成熟模板覆盖，必须说明“暂无成熟内置模板”，并建议改写到一个已支持模板方向。
- 当前内置模板清单：
{_inspiration_template_context()}
""".strip()


_INSPIRATION_GENERATION_RE = re.compile(
    r"(生成|制作|创建|开发|写|编写|输出|给我|做一个|做成).{0,18}(代码|源码|网页|html|css|javascript|js|python|组件|文件|页面产物|课堂工具)",
    re.IGNORECASE,
)
_CODE_ARTIFACT_RE = re.compile(
    r"```|<!doctype|<html\b|<script\b|<style\b|</div>|function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|class\s+\w+|import\s+.+from|def\s+\w+\s*\(",
    re.IGNORECASE,
)


def _is_inspiration_generation_request(message: str) -> bool:
    text = str(message or "").strip()
    if not text:
        return False
    return bool(_INSPIRATION_GENERATION_RE.search(text))


def _inspiration_boundary_reply(message: str) -> str:
    idea = _compact_inspiration_need(message)
    grounded = _template_grounded_inspiration_reply(message, boundary_need=idea)
    if grounded:
        return "\n".join(
            [
                "灵感助手不直接生成代码或网页产物；它只帮你把想法整理好。",
                "",
                grounded,
            ]
        )
    return "\n".join(
        [
            "灵感助手不直接生成代码或网页产物；它只帮你把想法整理好。",
            "",
            f"可放入生成框：{idea}",
            "",
            "建议保留：学生少看字、多操作；主模块做大；加入试听、拖拽、即时反馈和重来。",
        ]
    )


def _enforce_inspiration_reply_guardrails(message: str, reply: str) -> str:
    if _is_inspiration_generation_request(message):
        return _inspiration_boundary_reply(message)
    cleaned = _strip_code_blocks(str(reply or "").strip())
    if _CODE_ARTIFACT_RE.search(cleaned):
        return _inspiration_boundary_reply(message)
    if _should_strictly_rewrite_unmatched_inspiration(message, cleaned):
        return _strict_unmatched_template_reply(message)
    forbidden_claims = ["正在生成网页", "正在编写代码", "代码如下", "完整代码", "已生成代码"]
    for claim in forbidden_claims:
        cleaned = cleaned.replace(claim, "可以整理成生成需求")
    if _matched_production_template_id(message) and _mentions_unregistered_game_reply(message, cleaned):
        return _template_grounded_inspiration_reply(message)
    return cleaned or _inspiration_boundary_reply(message)


def _strip_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "这里不展示代码；我可以改成设计建议。", text).strip()


def _compact_inspiration_need(message: str) -> str:
    text = re.sub(r"\s+", " ", str(message or "")).strip()
    text = re.sub(r"(请|帮我|给我)?(直接)?(生成|制作|创建|开发|写|编写|输出)\s*", "", text)
    text = re.sub(r"(代码|源码|html|css|javascript|js|python|组件|文件)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(课堂工具){2,}", "课堂工具", text)
    text = text.strip("：:，,。 ")
    if not text:
        text = "设计一个适合学生操作的音乐课堂活动"
    if len(text) > 90:
        text = text[:89].rstrip() + "…"
    return f"请根据这个想法生成音乐课堂工具：{text}"


def _matched_production_template_id(message_or_template_id: str) -> str:
    text = str(message_or_template_id or "").strip()
    if text in INSPIRATION_TEMPLATE_LABELS:
        return text
    return detect_template_match_from_text(text)


def inspiration_suggested_need(message: str) -> str:
    text = str(message or "").strip()
    if not text or _looks_like_inspiration_chitchat(text):
        return ""
    template_id = _matched_production_template_id(text)
    if template_id:
        return INSPIRATION_TEMPLATE_NEED_HINTS.get(template_id, _compact_inspiration_need(text))
    if _should_offer_generic_suggested_need(text):
        return _compact_inspiration_need(text)
    return ""


def _with_inspiration_grounding(model_info: dict, message_or_template_id: str = "") -> dict:
    enriched = dict(model_info or {})
    enriched.update(
        {
            "template_grounding": "production_template_library",
            "matched_template_id": _matched_production_template_id(message_or_template_id),
            "grounding_mode": "strict",
        }
    )
    return enriched


def _template_grounded_inspiration_reply(message: str, *, boundary_need: str = "") -> str:
    text = str(message or "").strip()
    if not text:
        return ""
    template_id = _matched_production_template_id(text)
    if template_id:
        label = INSPIRATION_TEMPLATE_LABELS.get(template_id, template_id)
        reason = INSPIRATION_TEMPLATE_REASONS.get(template_id, "它是当前内置模板中最贴近这个音乐要素的玩法。")
        need = boundary_need or INSPIRATION_TEMPLATE_NEED_HINTS.get(template_id, _compact_inspiration_need(text))
        return "\n".join(
            [
                f"推荐内置模板：{label}",
                f"为什么贴合：{reason}",
                f"可放入生成框：{need}",
            ]
        )
    if _mentions_unsupported_expression_template(text):
        return "\n".join(
            [
                "非模板灵感：这个想法可以作为课堂讨论方向，但暂无成熟内置模板直接覆盖速度、力度或情绪变化。",
                "不能直接保证生成成品模板：请不要把它当作已支持的具体游戏模板。",
                "建议改写：如果要落到现有模板，可以改成节奏复刻训练速度稳定感，或节拍守卫训练强弱拍进入时机。",
            ]
        )
    return ""


def _strict_unmatched_template_reply(message: str) -> str:
    compact = _compact_inspiration_need(message)
    return "\n".join(
        [
            "非模板灵感：这个想法可以作为课堂讨论方向，但暂无成熟内置模板直接覆盖。",
            "不能直接保证生成成品模板：请不要把它当作已支持的具体游戏模板。",
            "建议改写：如果要落到现有生产游戏库，可以改成节奏复刻、节拍守卫、音高爬梯、唱名打靶、音色侦探、曲式寻宝或拼图创编工坊中的一个方向。",
            f"可放入生成框：{compact}",
        ]
    )


def _looks_like_inspiration_chitchat(text: str) -> bool:
    stripped = str(text or "").strip().lower()
    return stripped in {"你好", "嗨", "hello", "hi", "在吗", "谢谢", "好的", "嗯"} or len(stripped) <= 2


def _should_offer_generic_suggested_need(text: str) -> bool:
    return any(keyword in text for keyword in ("年级", "一年级", "二年级", "三年级", "四年级", "五年级", "六年级", "学生", "曲目", "歌曲", "乐句", "节奏", "音高", "音色", "创编", "活动", "游戏", "闯关"))


def _mentions_unregistered_game_reply(message: str, reply: str) -> bool:
    text = str(reply or "")
    if not any(keyword in text for keyword in ("模板", "飞行棋", "跑酷", "消消乐", "翻牌")):
        return False
    registered_labels = tuple(INSPIRATION_TEMPLATE_LABELS.values())
    return not any(label in text for label in registered_labels)


def _should_strictly_rewrite_unmatched_inspiration(message: str, reply: str) -> bool:
    if _matched_production_template_id(message):
        return False
    combined = f"{message}\n{reply}"
    if _mentions_unsupported_expression_template(combined):
        return True
    concrete_game_words = (
        "小游戏",
        "游戏",
        "玩法",
        "模板",
        "闯关",
        "飞行棋",
        "跑酷",
        "消消乐",
        "翻牌",
    )
    if not any(keyword in combined for keyword in concrete_game_words):
        return False
    registered_labels = tuple(INSPIRATION_TEMPLATE_LABELS.values())
    return not any(label in combined for label in registered_labels)


def _mentions_unsupported_expression_template(text: str) -> bool:
    return any(keyword in text for keyword in INSPIRATION_UNSUPPORTED_TEMPLATE_KEYWORDS)


def _latest_user_message(messages: list[dict[str, str]]) -> str:
    for item in reversed(messages):
        if item.get("role") == "user" and str(item.get("content") or "").strip():
            return str(item.get("content") or "").strip()
    return ""


def _json_from_text(text: str) -> dict:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()

    candidate = _extract_json_object_text(cleaned)
    for attempt in _json_parse_attempts(candidate):
        try:
            payload = json.loads(attempt)
            if not isinstance(payload, dict):
                raise ValueError("model response JSON is not an object")
            return payload
        except json.JSONDecodeError:
            continue
    # Run one final parse so callers get the most useful JSONDecodeError.
    payload = json.loads(candidate)
    if not isinstance(payload, dict):
        raise ValueError("model response JSON is not an object")
    return payload


def _extract_json_object_text(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1].strip()
    return text.strip()


def _json_parse_attempts(text: str) -> list[str]:
    normalized = (
        text.strip()
        .replace("\ufeff", "")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    attempts = [normalized]
    repaired = _repair_json_like_text(normalized)
    if repaired != normalized:
        attempts.append(repaired)
    return attempts


def _repair_json_like_text(text: str) -> str:
    repaired = text
    repaired = re.sub(r"//.*?$", "", repaired, flags=re.MULTILINE)
    repaired = re.sub(r"/\*[\s\S]*?\*/", "", repaired)
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)
    repaired = re.sub(r"([{\[,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)", r'\1"\2"\3', repaired)
    repaired = re.sub(r":\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: ': ' + json.dumps(match.group(1), ensure_ascii=False), repaired)
    repaired = re.sub(r"\[\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: "[" + json.dumps(match.group(1), ensure_ascii=False), repaired)
    repaired = re.sub(r",\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: ", " + json.dumps(match.group(1), ensure_ascii=False), repaired)
    return repaired.strip()


def _string_list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        cleaned = [str(item) for item in value if str(item).strip()]
        if cleaned:
            return cleaned
    return fallback


def _merge_unique_strings(values: list[str], additions: list[str]) -> list[str]:
    merged: list[str] = []
    for item in [*values, *additions]:
        text = str(item or "").strip()
        if text and text not in merged:
            merged.append(text)
    return merged


def _is_meta_lesson_check(text: str) -> bool:
    return any(
        marker in text
        for marker in ["是否服务于", "是否真正聚焦", "不是泛泛", "脱离教案", "页面只", "生成结果", "质量门槛"]
    )
