from __future__ import annotations

from copy import deepcopy
import json
import re
from typing import Any

from app.services.games.game_template_registry import get_game_template
from app.services.materials.music_element_adjustment_contract import filter_template_config_overrides
from app.services.music.pitch_catalog import pitch_tokens_from_text


PATCH_VERSION = "template_instance_patch_v1"
PATCH_OWNER = "lesson_template_personalizer"

LOCKED_PATCH_FIELDS = {
    "template_id",
    "engine",
    "scene_id",
    "runtime_shell",
    "runtime_component",
    "scene_config",
    "frontend_policy",
    "forbid_standalone_web_trio",
    "open_source_frontend",
}

COPY_PATCH_FIELDS = {
    "student_task_copy",
    "music_reason_prompts",
    "result_transfer_prompt",
}

KNOWN_INSTRUMENTS = ["笛子", "长笛", "二胡", "小提琴", "古筝", "钢琴", "木鱼", "小鼓", "人声"]


def build_template_instance_patch(
    *,
    template_id: str,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    lesson_adaptation: dict[str, Any],
    source_text: str = "",
) -> dict[str, Any]:
    """Build a one-off template instance patch for a lesson workflow.

    The patch is deliberately instance-scoped. It is never written back to the
    template registry or experience variant registry.
    """

    if not get_game_template(template_id):
        return _report(template_id, "skipped", {}, [], "unknown_template", "未命中可复用模板，跳过实例补丁。")

    entity_patch, entity_reason = _entity_patch_for_template(template_id, lesson_fit)
    if entity_patch:
        fallback_patch = _local_patch_for_lesson(
            template_id=template_id,
            lesson_context=lesson_context,
            lesson_fit=lesson_fit,
            lesson_adaptation=lesson_adaptation,
            source_text=source_text,
        )
        return sanitize_template_instance_patch(
            template_id,
            fallback_patch,
            source="music_element_binding",
            reason=entity_reason,
        )

    llm_error = ""
    llm_patch = _build_llm_patch(
        template_id=template_id,
        lesson_context=lesson_context,
        lesson_fit=lesson_fit,
        lesson_adaptation=lesson_adaptation,
        source_text=source_text,
    )
    if llm_patch.get("patch"):
        return sanitize_template_instance_patch(
            template_id,
            llm_patch["patch"],
            source="llm",
            reason=str(llm_patch.get("reason") or "根据教案生成模板实例补丁。"),
        )
    llm_error = str(llm_patch.get("error") or "")

    fallback_patch = _local_patch_for_lesson(
        template_id=template_id,
        lesson_context=lesson_context,
        lesson_fit=lesson_fit,
        lesson_adaptation=lesson_adaptation,
        source_text=source_text,
    )
    reason = "LLM 不可用，已用本地规则生成模板实例补丁。" if llm_error else "已用本地规则生成模板实例补丁。"
    report = sanitize_template_instance_patch(template_id, fallback_patch, source="local_fallback", reason=reason)
    if llm_error:
        report["llm_error"] = llm_error
    return report


def sanitize_template_instance_patch(
    template_id: str,
    raw_patch: dict[str, Any],
    *,
    source: str,
    reason: str,
) -> dict[str, Any]:
    rejected: list[str] = []
    if not isinstance(raw_patch, dict):
        return _report(template_id, "skipped", {}, [], source, reason)

    clean_input: dict[str, Any] = {}
    for key, value in raw_patch.items():
        if key in LOCKED_PATCH_FIELDS:
            rejected.append(key)
            continue
        clean_input[key] = value

    allowed = filter_template_config_overrides(template_id, clean_input)
    for key in COPY_PATCH_FIELDS:
        if key not in clean_input:
            continue
        value = clean_input[key]
        if key == "result_transfer_prompt" and isinstance(value, str) and value.strip():
            allowed[key] = value.strip()
        elif key in {"student_task_copy", "music_reason_prompts"} and isinstance(value, dict):
            compact = {str(k): v for k, v in value.items() if str(k).strip() and isinstance(v, (str, int, float, bool))}
            if compact:
                allowed[key] = compact

    for key in clean_input:
        if key not in allowed and key not in COPY_PATCH_FIELDS:
            rejected.append(key)
    rejected = sorted(set(rejected))
    status = "applied" if allowed else "skipped"
    return _report(template_id, status, allowed, rejected, source, reason)


def _build_llm_patch(
    *,
    template_id: str,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    lesson_adaptation: dict[str, Any],
    source_text: str,
) -> dict[str, Any]:
    try:
        from app.services.core.llm_config import llm_runtime_config
    except Exception as exc:
        return {"patch": {}, "error": f"llm_config_unavailable: {exc}"}
    config = llm_runtime_config()
    if not config.get("enabled"):
        return {"patch": {}, "error": "llm_disabled"}
    try:
        from openai import OpenAI

        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是音乐课堂游戏模板实例改编器。只输出 JSON，不写解释。"
                        "你的任务是为当前教案生成一次性的 template instance patch。"
                        "禁止修改 engine、scene_id、runtime_shell、scene_config、template_id。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "template_id": template_id,
                            "lesson_context": lesson_context,
                            "lesson_fit": lesson_fit,
                            "lesson_adaptation": lesson_adaptation,
                            "source_text": source_text,
                            "output_shape": {
                                "reason": "为什么这样改",
                                "patch": {
                                    "difficulty": "L1-L5 可选",
                                    "teacher_prompt": "教师提示",
                                    "student_task_copy": {"listen": "", "do": "", "pass": ""},
                                },
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={"type": "json_object"},
            timeout=20,
        )
        payload = _json_from_text(response.choices[0].message.content or "{}")
        return {
            "patch": payload.get("patch") if isinstance(payload.get("patch"), dict) else {},
            "reason": payload.get("reason") or "",
        }
    except Exception as exc:  # pragma: no cover - depends on optional external LLM.
        return {"patch": {}, "error": str(exc)}


def _local_patch_for_lesson(
    *,
    template_id: str,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    lesson_adaptation: dict[str, Any],
    source_text: str,
) -> dict[str, Any]:
    evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    material = lesson_fit.get("material_binding", {}) if isinstance(lesson_fit.get("material_binding"), dict) else {}
    focus = _first_text(
        evidence.get("music_element"),
        lesson_context.get("target_music_element"),
        lesson_adaptation.get("lesson_focus", {}).get("music_element") if isinstance(lesson_adaptation.get("lesson_focus"), dict) else "",
        source_text,
    )
    target_stage = _first_text(evidence.get("target_stage"), lesson_context.get("target_stage"), "课堂活动")
    segment = _first_text(material.get("selected_phrase_label"), evidence.get("segment_task"), "作品片段")
    patch: dict[str, Any] = {
        "music_concept": focus or "综合音乐感知",
        "teacher_prompt": f"先回到{segment}听辨{focus or '音乐重点'}，再进入游戏操作，最后回到{target_stage}复盘。",
        "student_task_copy": {
            "listen": f"听什么：听{segment}里的{focus or '音乐重点'}。",
            "do": "做什么：完成本关操作，并留意自己的音乐依据。",
            "pass": "怎样过关：操作正确后，说出你听到或做到的理由。",
        },
        "result_transfer_prompt": lesson_fit.get("transfer_task") or "通关后回到歌曲材料，用唱、拍、说或演奏复盘。",
    }
    entity_patch, _entity_reason = _entity_patch_for_template(template_id, lesson_fit)
    grade_text = _compact_join([lesson_context.get("grade_band"), source_text])
    if any(word in grade_text for word in ("低段", "一年级", "二年级", "入门", "简单")):
        patch.update({"difficulty": "L1", "round_count": 4, "pass_score": 0.72})
    elif any(word in grade_text for word in ("高段", "五年级", "六年级", "挑战", "较难")):
        patch.update({"difficulty": "L4", "round_count": 7, "pass_score": 0.84})

    text = _compact_join([source_text, focus, evidence.get("target_objective"), evidence.get("segment_task")])
    if template_id == "rhythm_echo_core":
        patch.update(_rhythm_patch(text))
    elif template_id == "beat_guardian_core":
        patch.update(_beat_patch(text))
    elif template_id == "pitch_ladder_core":
        patch.update(_pitch_patch(text))
    elif template_id == "solfege_target_core":
        patch.update(_solfege_patch(text))
    elif template_id == "timbre_detective_core":
        patch.update(_timbre_patch(text))
    elif template_id == "form_treasure_core":
        patch.update(_form_patch(text))
    elif template_id == "composition_puzzle_core":
        patch.update(_composition_patch(text))
    if entity_patch:
        patch.update(entity_patch)
    patch.pop("_entity_reason", None)
    return patch


def _entity_patch_for_template(template_id: str, lesson_fit: dict[str, Any]) -> tuple[dict[str, Any], str]:
    binding = lesson_fit.get("music_element_binding") if isinstance(lesson_fit.get("music_element_binding"), dict) else {}
    if binding.get("status") != "resolved":
        return {}, ""
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    reason = f"根据已解析音乐实体“{canonical.get('label') or canonical.get('id') or '音乐要素'}”改编模板实例。"
    if template_id == "rhythm_echo_core":
        playback = entity.get("playback") if isinstance(entity.get("playback"), dict) else {}
        steps = playback.get("pattern_steps") or entity.get("answer_tokens")
        if isinstance(steps, list):
            normalized = [str(item).strip() for item in steps if str(item or "").strip()]
            if normalized:
                return {"pattern_steps": normalized, "music_reason_prompts": {"entity": reason}}, reason
    if template_id == "pitch_ladder_core":
        melody = entity.get("target_melody")
        if isinstance(melody, list):
            pitches = [str(item).strip() for item in melody if str(item or "").strip()]
            if pitches:
                return {"pitch_range": pitches[:8]}, reason
    if template_id == "solfege_target_core":
        solfege = entity.get("target_solfege")
        if isinstance(solfege, list):
            pitches = [str(item).strip() for item in solfege if str(item or "").strip()]
            if pitches:
                return {"target_solfege": pitches[:8]}, reason
    if template_id == "timbre_detective_core":
        instruments = entity.get("instrument_pool")
        if isinstance(instruments, list):
            pool = [str(item).strip() for item in instruments if str(item or "").strip()]
            if len(pool) >= 2:
                return {"instrument_pool": pool[:6]}, reason
    if template_id == "form_treasure_core" and entity.get("form_type"):
        return {"form_type": str(entity.get("form_type")), "mode": "aba_treasure" if entity.get("form_type") == "ABA" else "repeat_contrast"}, reason
    if template_id == "composition_puzzle_core" and entity.get("scale_degrees"):
        degrees = [str(item).strip() for item in entity.get("scale_degrees", []) if str(item or "").strip()]
        if degrees:
            return {
                "mode": "melody_puzzle_creation",
                "melody_cards": degrees,
                "required_elements": degrees,
                "constraint_profile": "guided",
            }, reason
    return {}, ""


def _rhythm_patch(text: str) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    if "休止" in text:
        patch["pattern_steps"] = ["quarter", "rest", "eighth_pair"]
        patch["music_reason_prompts"] = {"missing": "休止处要安静，下一拍再进入。"}
    elif "切分" in text:
        patch["pattern_steps"] = ["quarter", "syncopation"]
    elif "附点" in text:
        patch["pattern_steps"] = ["dotted_quarter", "eighth_pair"]
    if any(word in text for word in ("接龙", "续接")):
        patch["mode"] = "echo_chain"
    elif any(word in text for word in ("身体", "拍腿", "跺脚", "律动")):
        patch["mode"] = "echo_body_percussion"
    return patch


def _beat_patch(text: str) -> dict[str, Any]:
    patch: dict[str, Any] = {"target_beats": [1]}
    if "三拍" in text or "3/4" in text:
        patch["meter"] = "3/4"
    elif "二拍" in text or "2/4" in text:
        patch["meter"] = "2/4"
    if "每拍" in text:
        patch["mode"] = "beat_defense"
    return patch


def _pitch_patch(text: str) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    pitches = _pitch_tokens_from_text(text)
    if pitches:
        patch["pitch_range"] = pitches
    if any(word in text for word in ("旋律", "上行", "下行", "级进", "跳进")):
        patch["mode"] = "melody_climb"
    elif "唱名" in text:
        patch["mode"] = "solfege_ladder"
    return patch


def _solfege_patch(text: str) -> dict[str, Any]:
    pitches = _pitch_tokens_from_text(text)
    return {"target_solfege": pitches} if pitches else {}


def _timbre_patch(text: str) -> dict[str, Any]:
    instruments = [item for item in KNOWN_INSTRUMENTS if item in text]
    patch: dict[str, Any] = {}
    if len(instruments) >= 2:
        patch["instrument_pool"] = instruments
    if any(word in text for word in ("家族", "管乐", "弦乐", "打击乐")):
        patch["mode"] = "family_sorting"
    return patch


def _form_patch(text: str) -> dict[str, Any]:
    if "回旋" in text:
        return {"form_type": "回旋", "mode": "rondo_treasure"}
    if "重复对比" in text or "重复与对比" in text:
        return {"form_type": "重复对比", "mode": "repeat_contrast"}
    if "ABA" in text.upper():
        return {"form_type": "ABA", "mode": "aba_treasure"}
    return {}


def _composition_patch(text: str) -> dict[str, Any]:
    if any(word in text for word in ("旋律节奏", "音符拼图", "综合")):
        return {"mode": "melody_rhythm_puzzle"}
    if any(word in text for word in ("旋律", "音级", "唱名")):
        return {"mode": "melody_puzzle_creation"}
    if any(word in text for word in ("节奏", "时值", "休止", "切分", "附点")):
        return {"mode": "rhythm_puzzle_composition"}
    return {}


def _pitch_tokens_from_text(text: str) -> list[str]:
    tokens = pitch_tokens_from_text(text)
    return tokens if len(tokens) >= 2 else []


def _json_from_text(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return {}
        try:
            payload = json.loads(match.group(0))
            return payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            return {}


def _report(
    template_id: str,
    status: str,
    patch: dict[str, Any],
    rejected_fields: list[str],
    source: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "version": PATCH_VERSION,
        "owner": PATCH_OWNER,
        "template_id": template_id,
        "source": source,
        "status": status,
        "patch": deepcopy(patch),
        "rejected_fields": list(rejected_fields),
        "reason": reason,
    }


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _compact_join(values: list[Any]) -> str:
    return " ".join(str(value or "").strip() for value in values if str(value or "").strip())
