from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.game_workflow_orchestrator import hard_blocking_quality_failures


def apply_generation_interventions(
    workflow: dict[str, Any],
    *,
    lesson_game_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run lesson-fit and frontend-presentation directors before publishing."""

    updated = deepcopy(workflow)
    trace: list[dict[str, str]] = []
    if isinstance(lesson_game_contract, dict) and lesson_game_contract:
        _apply_lesson_fit_intervention(updated, lesson_game_contract, trace)
    _apply_frontend_presentation_intervention(updated, lesson_game_contract or {}, trace)
    updated["intervention_trace"] = trace
    _append_intervention_gate(updated, lesson_game_contract)
    return updated


def _apply_lesson_fit_intervention(
    workflow: dict[str, Any],
    contract: dict[str, Any],
    trace: list[dict[str, str]],
) -> None:
    blueprint = workflow.setdefault("gameplay_blueprint", {})
    experience = workflow.setdefault("experience_script", {})
    render_spec = workflow.setdefault("render_spec", {})
    proposal_card = workflow.setdefault("proposal_card", {})
    lesson_adaptation = workflow.setdefault("lesson_adaptation", {})

    focus = _first_text(
        contract.get("music_focus"),
        contract.get("lesson_adaptation", {}).get("lesson_focus", {}).get("music_element")
        if isinstance(contract.get("lesson_adaptation"), dict)
        else "",
        proposal_card.get("music_element"),
        blueprint.get("music_focus"),
    )
    stage = _first_text(contract.get("selected_stage"), blueprint.get("selected_stage"), proposal_card.get("stage"))
    selected_task = _first_text(contract.get("selected_task"), contract.get("game_mechanic"), blueprint.get("prompt"))
    game_name = _first_text(contract.get("game_name"), blueprint.get("student_facing_name"), proposal_card.get("title"))
    win_condition = _first_text(contract.get("win_condition"), blueprint.get("win_condition"))
    transfer = _first_text(
        contract.get("playable_game", {}).get("learning_transfer", {}).get("classroom_transfer")
        if isinstance(contract.get("playable_game"), dict)
        else "",
        proposal_card.get("transfer_task"),
        "通关后回到课堂，用唱、拍、说或动作说明你的音乐依据。",
    )

    lesson_prompt = _lesson_prompt(stage=stage, focus=focus, selected_task=selected_task)
    blueprint.update(
        {
            "student_facing_name": game_name or blueprint.get("student_facing_name") or "本课音乐游戏",
            "music_focus": focus or blueprint.get("music_focus", ""),
            "lesson_goal": contract.get("lesson_goal") or blueprint.get("lesson_goal", ""),
            "selected_stage": stage or blueprint.get("selected_stage", ""),
            "prompt": lesson_prompt,
            "win_condition": win_condition or blueprint.get("win_condition", ""),
            "lesson_fit_applied": True,
            "lesson_specificity": {
                "stage": stage,
                "music_focus": focus,
                "selected_task": selected_task,
                "transfer": transfer,
            },
        }
    )
    if contract.get("student_actions"):
        blueprint["student_actions"] = list(contract.get("student_actions", []))[:6]
    learning_transfer = blueprint.get("learning_transfer", {}) if isinstance(blueprint.get("learning_transfer"), dict) else {}
    learning_transfer["classroom_transfer"] = transfer
    blueprint["learning_transfer"] = learning_transfer

    experience["opening_hook"] = _opening_hook(stage=stage, focus=focus, game_name=game_name)
    tutorial = experience.get("tutorial", {}) if isinstance(experience.get("tutorial"), dict) else {}
    tutorial["first_action_hint"] = _tutorial_hint(focus=focus, selected_task=selected_task)
    experience["tutorial"] = tutorial
    experience["closure_prompt"] = transfer
    experience["lesson_fit_applied"] = True

    screen = render_spec.setdefault("screen_structure", {})
    screen["lesson_anchor"] = {
        "stage": stage,
        "music_focus": focus,
        "selected_task": selected_task,
        "student_visible": True,
    }
    render_spec["student_task_copy"] = {
        "listen": _listen_copy(focus),
        "do": selected_task or "完成本关操作。",
        "pass": win_condition or "说出你的音乐依据。",
    }
    proposal_card["fit_summary"] = proposal_card.get("fit_summary") or f"围绕“{focus or '本课重点'}”生成课堂游戏。"
    lesson_adaptation["intervention_status"] = "applied_to_student_runtime"
    trace.append(
        {
            "agent": "lesson_fit_director",
            "action": "rewrote_student_task_from_lesson_contract",
            "detail": f"{stage or '课堂环节'} · {focus or '音乐重点'}",
        }
    )


def _apply_frontend_presentation_intervention(
    workflow: dict[str, Any],
    contract: dict[str, Any],
    trace: list[dict[str, str]],
) -> None:
    pack = workflow.setdefault("presentation_pack", {})
    theme = workflow.setdefault("theme_pack", {})
    blueprint = workflow.get("gameplay_blueprint", {}) if isinstance(workflow.get("gameplay_blueprint"), dict) else {}
    focus = _first_text(
        contract.get("music_focus") if isinstance(contract, dict) else "",
        blueprint.get("music_focus"),
    )
    stage = _first_text(
        contract.get("selected_stage") if isinstance(contract, dict) else "",
        blueprint.get("selected_stage"),
    )
    scene = pack.get("scene", {}) if isinstance(pack.get("scene"), dict) else {}
    scene["lesson_focus"] = focus
    scene["lesson_stage"] = stage
    if stage and focus:
        scene["setting"] = f"{stage} · {focus}"
    pack["scene"] = scene
    pack["source"] = "lesson_fit_and_frontend_intervention" if contract else "frontend_intervention"
    pack["intervention_applied"] = True
    pack["presentation_directive"] = {
        "student_first": True,
        "avoid_template_shell": True,
        "show_lesson_anchor": bool(focus or stage),
        "locked_gameplay": blueprint.get("operation_type", ""),
    }
    asset_manifest = pack.get("asset_manifest", {}) if isinstance(pack.get("asset_manifest"), dict) else {}
    asset_manifest["lesson_focus"] = focus
    asset_manifest["lesson_stage"] = stage
    pack["asset_manifest"] = asset_manifest
    theme_scene = theme.get("scene", {}) if isinstance(theme.get("scene"), dict) else {}
    if stage and focus:
        theme_scene["setting"] = f"{stage} · {focus}"
    theme["scene"] = theme_scene
    trace.append(
        {
            "agent": "frontend_presentation_director",
            "action": "rewrote_presentation_pack_for_student_runtime",
            "detail": pack.get("layout_variant", "") or pack.get("skin_family", ""),
        }
    )


def _append_intervention_gate(workflow: dict[str, Any], lesson_game_contract: dict[str, Any] | None) -> None:
    gates = workflow.setdefault("quality_gates", [])
    if not isinstance(gates, list):
        return
    gates.append(
        {
            "id": "generation_intervention_applied",
            "label": "教案与前端介入",
            "status": "pass",
            "detail": (
                "已在模板发布前运行教案贴合介入和前端表现介入。"
                if lesson_game_contract
                else "已在模板发布前运行前端表现介入。"
            ),
        }
    )
    summary = workflow.setdefault("quality_summary", {})
    if isinstance(summary, dict):
        summary["total"] = len(gates)
        summary["pass_count"] = sum(1 for gate in gates if isinstance(gate, dict) and gate.get("status") == "pass")
        summary["blocking_failures"] = [gate for gate in gates if isinstance(gate, dict) and gate.get("status") == "fail"]
        summary["hard_blocking_failures"] = hard_blocking_quality_failures(gates)


def _lesson_prompt(*, stage: str, focus: str, selected_task: str) -> str:
    parts = []
    if stage:
        parts.append(f"放在“{stage}”")
    if focus:
        parts.append(f"围绕“{focus}”")
    if selected_task:
        parts.append(_trim_sentence_end(selected_task))
    return "本关任务：" + "，".join(parts) + "。" if parts else "本关任务：先听清音乐，再完成挑战。"


def _opening_hook(*, stage: str, focus: str, game_name: str) -> str:
    if focus and stage:
        return f"{game_name or '本课游戏'}开始了：先在“{stage}”里听出“{focus}”，再完成挑战。"
    if focus:
        return f"{game_name or '本课游戏'}开始了：先听出“{focus}”，再完成挑战。"
    return "先听清这节课的音乐任务，再开始挑战。"


def _tutorial_hint(*, focus: str, selected_task: str) -> str:
    if selected_task:
        return f"先听一遍，再完成：{selected_task}"
    if focus:
        return f"先听一遍，注意“{focus}”的变化。"
    return "先试听目标，再开始第一步操作。"


def _listen_copy(focus: str) -> str:
    return f"听出“{focus}”" if focus else "听清目标音乐"


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _trim_sentence_end(text: str) -> str:
    return str(text or "").strip().rstrip("。.!！")
