from __future__ import annotations

from copy import deepcopy
from typing import Any


RHYTHM_ERROR_FEEDBACK = [
    {"error_type": "early", "music_meaning": "早了", "feedback": "抢拍了：先等到拍点再出手。"},
    {"error_type": "late", "music_meaning": "晚了", "feedback": "拖拍了：心里的稳定拍要往前带一点。"},
    {"error_type": "missing", "music_meaning": "漏拍", "feedback": "漏拍了：目标节奏中间少了一下。"},
    {"error_type": "wrong_order", "music_meaning": "顺序错", "feedback": "顺序错了：再听长短和休止的位置。"},
    {"error_type": "duration_error", "music_meaning": "时值错", "feedback": "时值不稳：长音、短音和休止要分清。"},
]


def build_game_design(instance: dict[str, Any], *, activity_spec: dict[str, Any] | None = None) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if template_id == "rhythm_echo_core":
        return _rhythm_echo_game_design(instance, activity_spec=activity_spec or {})
    return {
        "version": "game_design_v1",
        "template_id": template_id,
        "mechanic_contract": {
            "mechanic_id": f"{template_id}_mechanic",
            "operation": config.get("interaction_model", ""),
            "answer_rule": "由模板运行时和 music-truth.json 提供正式判定。",
        },
        "music_learning_behavior": config.get("music_concept", "音乐要素感知与表达"),
        "error_feedback": [],
        "loop_duration_minutes": 3,
        "age_fit": _age_fit(config, activity_spec or {}),
    }


def _rhythm_echo_game_design(
    instance: dict[str, Any],
    *,
    activity_spec: dict[str, Any],
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    reason_prompts = config.get("music_reason_prompts") if isinstance(config.get("music_reason_prompts"), dict) else {}
    feedback = []
    for item in RHYTHM_ERROR_FEEDBACK:
        merged = deepcopy(item)
        if reason_prompts.get(item["error_type"]):
            merged["feedback"] = reason_prompts[item["error_type"]]
        feedback.append(merged)
    return {
        "version": "game_design_v1",
        "template_id": "rhythm_echo_core",
        "mechanic_contract": {
            "mechanic_id": "rhythm_echo_replay",
            "operation": "listen_memorize_replay",
            "student_action": "先听目标节奏，再用点击、键盘或身体动作按拍点复刻。",
            "answer_rule": "输入事件按 pattern_timeline 与 judgement_windows 判定早、晚、漏、顺序和时值错误。",
            "runtime_loop": ["listen", "ready", "replay", "feedback", "retry_or_next"],
        },
        "music_learning_behavior": "听辨目标节奏并按拍点复刻",
        "correct_condition": {
            "required_accuracy": config.get("required_accuracy") or config.get("pass_score") or 0.8,
            "timing_tolerance_ms": config.get("timing_tolerance_ms") or 180,
            "pattern_steps": deepcopy(config.get("pattern_steps") or []),
        },
        "error_feedback": feedback,
        "loop_duration_minutes": _loop_duration(config),
        "age_fit": _age_fit(config, activity_spec),
    }


def _loop_duration(config: dict[str, Any]) -> int:
    round_count = int(config.get("round_count") or 6)
    if round_count <= 3:
        return 3
    if round_count <= 6:
        return 4
    return 5


def _age_fit(config: dict[str, Any], activity_spec: dict[str, Any]) -> dict[str, Any]:
    stage = str(activity_spec.get("stage") or config.get("grade_band") or "").strip()
    lower_primary = "低" in stage or "一" in stage or "二" in stage
    return {
        "stage": stage or "小学低段",
        "first_screen_rule": "一眼看到听、拍、过关反馈" if lower_primary else "先听辨，再复刻并解释节奏依据",
        "text_density": "low" if lower_primary else "medium",
    }
