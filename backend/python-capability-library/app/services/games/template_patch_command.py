# 把教师自然语言修改要求转成安全、可执行的模板修改指令
# 它强调模型只能提出修改意图，真正是否允许修改，要由本地规则和模板约束决定；代码中也明确禁止通过修改指令直接“重写网页”。
from __future__ import annotations

from copy import deepcopy
import re
from collections.abc import Callable
from typing import Any
import json
import urllib.error
import urllib.request

from app.services.games.game_template_registry import build_game_instance
from app.services.games.game_variant_spec import teacher_confirmation_cards_from_variant_spec, template_capability_profile
from app.services.core.llm_config import llm_runtime_config
from app.services.materials.music_element_resolver import retrieve_music_element_candidates
from app.services.music.pitch_catalog import pitch_tokens_from_text


PATCH_COMMAND_VERSION = "patch_command_v1"
PATCH_INTENT_VERSION = "dialog_patch_intent_v1"
LOCKED_CONFIG_FIELDS = {"template_id", "engine", "scene_id", "runtime_shell", "runtime_component"}


DialogPatchIntentProvider = Callable[[dict[str, Any]], dict[str, Any]]


def build_llm_dialog_patch_intent_provider(*, enabled: bool = False) -> DialogPatchIntentProvider | None:
    if not enabled:
        return None
    config = llm_runtime_config()
    if not config.get("enabled"):
        return None

    def provider(context: dict[str, Any]) -> dict[str, Any]:
        return _call_patch_intent_model(context, config)

    return provider


def build_dialog_patch_intent(
    workflow: dict[str, Any],
    revision: str,
    *,
    intent_provider: DialogPatchIntentProvider | None = None,
) -> dict[str, Any]:
    local_intent = _build_local_dialog_patch_intent(workflow, revision)
    if intent_provider is None:
        return local_intent
    provider_payload: dict[str, Any]
    try:
        provider_payload = intent_provider(_intent_provider_context(workflow, local_intent))
    except Exception as exc:
        return _intent_with_provider_rejection(local_intent, f"intent_provider_error:{exc.__class__.__name__}")
    normalized = _normalize_provider_intent(provider_payload, local_intent)
    if not normalized:
        return _intent_with_provider_rejection(local_intent, "unsafe_intent_provider_output")
    return normalized


def _build_local_dialog_patch_intent(workflow: dict[str, Any], revision: str) -> dict[str, Any]:
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or workflow.get("proposal_card", {}).get("template_id") or "")
    text = str(revision or "").strip()
    round_no = _round_number_from_text(text)
    segment_no = _segment_number_from_text(text)
    retrieval = retrieve_music_element_candidates(semantic_text=text, song_material={}, template_id=template_id)
    selected_candidate = _selected_entity_candidate(retrieval, template_id)
    music_entity = _intent_music_entity(template_id, text, selected_candidate, round_no=round_no, segment_no=segment_no)
    return {
        "version": PATCH_INTENT_VERSION,
        "template_id": template_id,
        "teacher_revision": text,
        "target_scope": _target_scope(text),
        "action_type": _intent_action_type(text, music_entity),
        "target": _intent_target(round_no=round_no, segment_no=segment_no),
        "music_entity": music_entity,
        "difficulty": _intent_difficulty(text),
        "presentation": _intent_presentation(text),
        "grounding": {
            "source": "local_rule_parser",
            "music_element_retrieval": retrieval,
            "selected_entity_candidate": selected_candidate,
        },
        "execution_policy": {
            "llm_may_propose": True,
            "local_executor_must_validate": True,
            "use_template_capability_profile": True,
            "forbid_webpage_rewrite": True,
            "requires_full_regeneration_default": False,
        },
    }


def _intent_provider_context(workflow: dict[str, Any], local_intent: dict[str, Any]) -> dict[str, Any]:
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    return {
        "version": "dialog_patch_intent_provider_context_v1",
        "template_id": local_intent.get("template_id", ""),
        "teacher_revision": local_intent.get("teacher_revision", ""),
        "local_intent": deepcopy(local_intent),
        "template_capability": template_capability_profile(str(local_intent.get("template_id") or "")),
        "current_config": deepcopy(config),
        "allowed_output_version": PATCH_INTENT_VERSION,
        "policy": deepcopy(local_intent.get("execution_policy", {})),
    }


def _normalize_provider_intent(provider_payload: dict[str, Any], local_intent: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(provider_payload, dict):
        return None
    if provider_payload.get("version") != PATCH_INTENT_VERSION:
        return None
    if str(provider_payload.get("template_id") or "") != str(local_intent.get("template_id") or ""):
        return None
    if str(provider_payload.get("action_type") or "") == "rewrite_webpage":
        return None
    policy = provider_payload.get("execution_policy") if isinstance(provider_payload.get("execution_policy"), dict) else {}
    if policy.get("forbid_webpage_rewrite") is False:
        return None
    normalized = deepcopy(local_intent)
    for key in ("target_scope", "action_type", "target", "music_entity", "difficulty", "presentation"):
        if key in provider_payload:
            normalized[key] = deepcopy(provider_payload[key])
    normalized["teacher_revision"] = str(provider_payload.get("teacher_revision") or local_intent.get("teacher_revision") or "")
    grounding = provider_payload.get("grounding") if isinstance(provider_payload.get("grounding"), dict) else {}
    fallback_grounding = local_intent.get("grounding") if isinstance(local_intent.get("grounding"), dict) else {}
    normalized["grounding"] = {
        **deepcopy(grounding),
        "source": str(grounding.get("source") or "llm_intent_provider"),
        "fallback_source": str(fallback_grounding.get("source") or "local_rule_parser"),
        "music_element_retrieval": deepcopy(fallback_grounding.get("music_element_retrieval", {})),
        "selected_entity_candidate": deepcopy(fallback_grounding.get("selected_entity_candidate", {})),
    }
    normalized["execution_policy"] = _safe_execution_policy(local_intent, policy)
    return normalized


def _safe_execution_policy(local_intent: dict[str, Any], provider_policy: dict[str, Any]) -> dict[str, Any]:
    local_policy = local_intent.get("execution_policy") if isinstance(local_intent.get("execution_policy"), dict) else {}
    return {
        **deepcopy(local_policy),
        **{key: deepcopy(value) for key, value in provider_policy.items() if key not in {"local_executor_must_validate", "forbid_webpage_rewrite"}},
        "llm_may_propose": True,
        "local_executor_must_validate": True,
        "use_template_capability_profile": True,
        "forbid_webpage_rewrite": True,
        "requires_full_regeneration_default": False,
    }


def _intent_with_provider_rejection(local_intent: dict[str, Any], reason: str) -> dict[str, Any]:
    intent = deepcopy(local_intent)
    grounding = intent.get("grounding") if isinstance(intent.get("grounding"), dict) else {}
    grounding["provider_rejected"] = reason
    intent["grounding"] = grounding
    return intent


def _call_patch_intent_model(context: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    messages = _patch_intent_messages(context)
    if config.get("provider") == "chat_ecnu":
        return _call_chat_ecnu_patch_intent_model(config, messages)
    return _call_openai_compatible_patch_intent_model(config, messages)


def _patch_intent_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    system = (
        "你是音乐游戏对话修改意图解析器。只输出 JSON，不要解释。"
        "你只能生成 dialog_patch_intent_v1。"
        "你可以理解老师想改什么，但不能请求重写网页，不能关闭本地验证。"
        "本地执行器会根据模板能力图谱验证你的输出。"
    )
    user = json.dumps(
        {
            "task": "把老师的自然语言修改请求转成 dialog_patch_intent_v1。",
            "schema": {
                "version": "dialog_patch_intent_v1",
                "template_id": "必须等于输入 template_id",
                "teacher_revision": "老师原话",
                "target_scope": ["round_2/music_material/template_instance 等"],
                "action_type": "replace_music_entity|adjust_difficulty|adjust_presentation|revise_template_instance",
                "target": {"kind": "round|segment|template_instance"},
                "music_entity": {"entity_type": "可为空", "value": "可为数组或对象"},
                "difficulty": {},
                "presentation": {},
                "grounding": {"source": "llm_intent_provider"},
                "execution_policy": {
                    "llm_may_propose": True,
                    "local_executor_must_validate": True,
                    "use_template_capability_profile": True,
                    "forbid_webpage_rewrite": True,
                    "requires_full_regeneration_default": False,
                },
            },
            "context": context,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _call_openai_compatible_patch_intent_model(config: dict[str, Any], messages: list[dict[str, str]]) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"], timeout=20.0)
    response = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        max_tokens=900,
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return _json_from_text(content)


def _call_chat_ecnu_patch_intent_model(config: dict[str, Any], messages: list[dict[str, str]]) -> dict[str, Any]:
    payload = {
        "messages": messages,
        "stream": False,
        "model": config["model"],
    }
    request = urllib.request.Request(
        config["chat_completions_url"],
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"ChatECNU patch intent failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"ChatECNU patch intent connection failed: {exc.reason}") from exc
    payload = json.loads(raw)
    return _json_from_text(_chat_completion_content(payload))


def _chat_completion_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and message.get("content") is not None:
                return str(message.get("content") or "{}")
            if first.get("text") is not None:
                return str(first.get("text") or "{}")
    data = payload.get("data")
    if isinstance(data, dict):
        return _chat_completion_content(data)
    if payload.get("content") is not None:
        return str(payload.get("content") or "{}")
    return "{}"


def _json_from_text(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                payload = json.loads(raw[start : end + 1])
                return payload if isinstance(payload, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}


def build_patch_command(
    workflow: dict[str, Any],
    revision: str,
    *,
    intent_provider: DialogPatchIntentProvider | None = None,
) -> dict[str, Any]:
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or workflow.get("proposal_card", {}).get("template_id") or "")
    text = str(revision or "").strip()
    operations: list[dict[str, Any]] = []
    dialog_intent = build_dialog_patch_intent(workflow, text, intent_provider=intent_provider)
    target_scope = dialog_intent["target_scope"]
    grounding = dialog_intent.get("grounding", {}) if isinstance(dialog_intent.get("grounding"), dict) else {}
    retrieval = grounding.get("music_element_retrieval", {})
    selected_candidate = grounding.get("selected_entity_candidate", {})
    capability_check = _template_capability_check(template_id, text, selected_candidate)
    rejections: list[dict[str, Any]] = []
    if capability_check.get("status") == "rejected":
        rejections.append(
            {
                "reason": "unsupported_music_element_for_template",
                "template_id": template_id,
                "requested_music_element": capability_check.get("requested_music_element", ""),
                "recommended_template_id": capability_check.get("recommended_template_id", ""),
            }
        )
        return {
            "version": PATCH_COMMAND_VERSION,
            "intent": "revise_template_instance",
            "strategy": "template_instance_config_patch",
            "template_id": template_id,
            "revision": text,
            "target_scope": target_scope,
            "operations": [],
            "dialog_patch_intent": dialog_intent,
            "music_element_retrieval": retrieval,
            "selected_entity_candidate": selected_candidate,
            "entity_application": {},
            "capability_check": capability_check,
            "rejections": rejections,
            "patch_result": _patch_result(
                template_id=template_id,
                revision=text,
                operations=[],
                rejections=rejections,
                rejected_paths=[],
                entity_application={},
            ),
            "locked_fields": ["template_id", "engine", "scene_id", "runtime_shell", "runtime_component"],
            "requires_full_regeneration": False,
        }

    if any(token in text for token in ("简单", "容易", "低年级", "太难", "第一关")) or dialog_intent.get("difficulty"):
        operations.append({"op": "set", "path": "config.difficulty", "value": "L1"})
        current_round_count = config.get("round_count")
        if isinstance(current_round_count, (int, float)):
            round_count = max(1, int(current_round_count) - 1)
        else:
            round_count = 5
        operations.append({"op": "set", "path": "config.round_count", "value": round_count})
        operations.append({"op": "set", "path": "presentation_pack.motion_profile.tempo", "value": "gentle"})

    explicit_round_count = _round_count_from_text(text)
    if explicit_round_count is not None:
        operations.append({"op": "set", "path": "config.round_count", "value": explicit_round_count})

    material_operations = _music_material_operations(template_id, text, config, round_no=_round_number_from_text(text))
    operations.extend(material_operations)
    operations.extend(_intent_entity_operations(template_id, dialog_intent, config))
    operations.extend(_entity_grounded_operations(template_id, selected_candidate, text))
    entity_application = _entity_application(template_id, selected_candidate, operations)
    if not entity_application:
        entity_application = _intent_entity_application(template_id, dialog_intent, operations)

    lowered = text.lower()
    if any(token in text for token in ("按钮", "更大", "放大", "大一点")) or "button" in lowered:
        operations.extend(
            [
                {"op": "set", "path": "config.copy_budget.button_size", "value": "large"},
                {"op": "set", "path": "presentation_pack.css_variables.--arcade-scale", "value": "1.16"},
                {"op": "set", "path": "presentation_pack.css_variables.--arcade-button-min", "value": "64px"},
                {"op": "set", "path": "presentation_pack.hud_layout.primary_action", "value": "large_touch"},
            ]
        )

    if any(token in text for token in ("皮肤", "风格", "颜色", "更像", "主题")):
        operations.extend(
            [
                {"op": "set", "path": "presentation_pack.scene.revision_note", "value": text},
                {"op": "set", "path": "theme_pack.revision_note", "value": text},
            ]
        )

    return {
        "version": PATCH_COMMAND_VERSION,
        "intent": "revise_template_instance",
        "strategy": "template_instance_config_patch",
        "template_id": template_id,
        "revision": text,
        "target_scope": target_scope,
        "operations": operations,
        "dialog_patch_intent": dialog_intent,
        "music_element_retrieval": retrieval,
        "selected_entity_candidate": selected_candidate,
        "entity_application": entity_application,
        "capability_check": capability_check,
        "rejections": rejections,
        "patch_result": _patch_result(
            template_id=template_id,
            revision=text,
            operations=operations,
            rejections=rejections,
            rejected_paths=[],
            entity_application=entity_application,
        ),
        "locked_fields": ["template_id", "engine", "scene_id", "runtime_shell", "runtime_component"],
        "requires_full_regeneration": False,
    }


def apply_patch_command_to_workflow(workflow: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(workflow)
    rejected_paths: list[str] = []
    touched_config = False
    template_id = _workflow_template_id(updated, command)
    capability = template_capability_profile(template_id)
    for operation in command.get("operations", []) if isinstance(command.get("operations"), list) else []:
        if not isinstance(operation, dict):
            continue
        if operation.get("op") == "form_segment_patch":
            _apply_form_segment_patch(updated, operation)
            _sync_form_segment_patch_to_variant_spec(updated, operation)
            continue
        if operation.get("op") == "round_patch":
            _apply_round_patch(updated, operation)
            _sync_round_patch_to_variant_spec(updated, operation)
            continue
        if operation.get("op") != "set":
            continue
        path = str(operation.get("path") or "").strip()
        if not path or _is_locked_path(path, capability):
            if path:
                rejected_paths.append(path)
            continue
        if not _is_allowed_patch_path(path, capability):
            rejected_paths.append(path)
            continue
        if not _is_allowed_patch_value(path, operation.get("value"), capability):
            rejected_paths.append(path)
            continue
        _set_workflow_path(updated, path, operation.get("value"))
        _sync_game_variant_spec(updated, path, operation.get("value"))
        if path.startswith("config."):
            touched_config = True
    if touched_config:
        _renormalize_template_instance_config(updated)
    _sync_entity_application_contract(updated, command)
    _sync_teacher_confirmation_edit(updated, command)
    _sync_game_variant_execution_plan(updated, template_id)

    updated["template_revision"] = {
        "instance_scoped": True,
        "template_source_changed": False,
        "revision": command.get("revision", ""),
        "changed_surface": "patch_command",
        "patch_command": deepcopy(command),
        "entity_application": deepcopy(command.get("entity_application") or {}),
        "rejected_paths": rejected_paths,
        "patch_result": _patch_result(
            template_id=template_id,
            revision=str(command.get("revision") or ""),
            operations=command.get("operations") if isinstance(command.get("operations"), list) else [],
            rejections=command.get("rejections") if isinstance(command.get("rejections"), list) else [],
            rejected_paths=rejected_paths,
            entity_application=command.get("entity_application") if isinstance(command.get("entity_application"), dict) else {},
        ),
    }
    _record_patch_rejection_revision(updated, command, rejected_paths, template_id)
    _sync_frontend_execution_contract(updated)
    return updated


def _sync_entity_application_contract(workflow: dict[str, Any], command: dict[str, Any]) -> None:
    entity_application = command.get("entity_application") if isinstance(command.get("entity_application"), dict) else {}
    if not entity_application:
        return
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    spec["entity_application"] = deepcopy(entity_application)
    variant_parameters = spec.setdefault("variant_parameters", {})
    if isinstance(variant_parameters, dict) and isinstance(entity_application.get("game_parameters"), dict):
        variant_parameters.update(deepcopy(entity_application.get("game_parameters", {})))
    slot_bindings = spec.setdefault("slot_bindings", {})
    if isinstance(slot_bindings, dict) and isinstance(entity_application.get("slot_bindings"), dict):
        slot_bindings.update(deepcopy(entity_application.get("slot_bindings", {})))

    render_spec = workflow.get("render_spec") if isinstance(workflow.get("render_spec"), dict) else {}
    if render_spec:
        execution = render_spec.setdefault("music_entity_execution", {})
        if isinstance(execution, dict):
            execution["entity_application"] = deepcopy(entity_application)
            execution["variant_parameters"] = deepcopy(variant_parameters)
            execution["slot_bindings"] = deepcopy(slot_bindings)


def _sync_teacher_confirmation_edit(workflow: dict[str, Any], command: dict[str, Any]) -> None:
    spec = workflow.get("game_variant_spec") if isinstance(workflow.get("game_variant_spec"), dict) else {}
    if not spec:
        return
    gates = spec.get("confirmation_gates") if isinstance(spec.get("confirmation_gates"), list) else []
    if not gates or all(isinstance(gate, dict) and gate.get("status") == "confirmed" for gate in gates):
        return
    entity_application = (
        spec.get("entity_application") if isinstance(spec.get("entity_application"), dict) else {}
    )
    if not entity_application or entity_application.get("confirmation_status") != "confirmed_by_teacher_revision":
        return
    if command.get("patch_result", {}).get("status") == "rejected":
        return

    for gate in gates:
        if not isinstance(gate, dict) or gate.get("status") == "confirmed":
            continue
        gate["status"] = "confirmed"
        gate["confirmed_value"] = _confirmed_value_for_gate(gate, entity_application)
        gate["confirmed_by"] = "teacher_revision"
        gate.pop("confirmation_error", None)
    spec["confirmation_gates"] = gates
    spec["teacher_confirmation_cards"] = teacher_confirmation_cards_from_variant_spec(spec)
    spec["requires_teacher_confirmation"] = False
    spec["confirmation_reason"] = ""
    if isinstance(entity_application, dict):
        entity_application["requires_teacher_confirmation"] = False
        entity_application["confirmation_reason"] = ""
        spec["entity_application"] = entity_application
    workflow["game_variant_spec"] = spec


def _confirmed_value_for_gate(gate: dict[str, Any], entity_application: dict[str, Any]) -> Any:
    entity_type = str(gate.get("entity_type") or entity_application.get("entity_type") or "")
    parameters = (
        entity_application.get("game_parameters")
        if isinstance(entity_application.get("game_parameters"), dict)
        else {}
    )
    slots = (
        entity_application.get("slot_bindings")
        if isinstance(entity_application.get("slot_bindings"), dict)
        else {}
    )
    if entity_type == "rhythm_pattern":
        return deepcopy(
            parameters.get("pattern_steps")
            or slots.get("rhythm.pattern_steps")
            or _first_slot_value(slots, ".target_rhythm")
            or gate.get("proposed_value")
        )
    if entity_type == "pitch_motion":
        return deepcopy(
            _first_slot_value(slots, ".target_melody")
            or parameters.get("pitch_range")
            or gate.get("proposed_value")
        )
    if entity_type == "solfege_set":
        return deepcopy(
            parameters.get("target_solfege")
            or _first_slot_value(slots, ".target_solfege")
            or gate.get("proposed_value")
        )
    if entity_type == "meter":
        return _drop_empty(
            {
                "meter": parameters.get("meter"),
                "target_beats": deepcopy(parameters.get("target_beats")),
                "accent_pattern": deepcopy(slots.get("meter.accent_pattern")),
                "beat_count": slots.get("meter.beat_count"),
            }
        ) or deepcopy(gate.get("proposed_value"))
    if entity_type == "timbre_set":
        return _drop_empty(
            {
                "instrument_pool": deepcopy(parameters.get("instrument_pool")),
                "timbre_traits": deepcopy(parameters.get("timbre_traits")),
                "comparison_pairs": deepcopy(slots.get("timbre.comparison_pairs")),
                "trait_targets": deepcopy(slots.get("timbre.trait_targets")),
            }
        ) or deepcopy(gate.get("proposed_value"))
    if entity_type == "form_structure":
        return deepcopy(
            parameters.get("form_type")
            or slots.get("form.answer_pattern")
            or _first_slot_value(slots, ".form_label")
            or gate.get("proposed_value")
        )
    if entity_type == "composition_material":
        return _drop_empty(
            {
                "melody_cards": deepcopy(parameters.get("melody_cards")),
                "rhythm_cards": deepcopy(parameters.get("rhythm_cards")),
                "required_elements": deepcopy(parameters.get("required_elements")),
                "scale_degrees": deepcopy(slots.get("composition.scale_degrees")),
            }
        ) or deepcopy(gate.get("proposed_value"))
    if len(parameters) == 1:
        return deepcopy(next(iter(parameters.values())))
    if parameters:
        return deepcopy(parameters)
    if len(slots) == 1:
        return deepcopy(next(iter(slots.values())))
    return deepcopy(slots or gate.get("proposed_value"))


def _first_slot_value(slots: dict[str, Any], suffix: str) -> Any:
    for key, value in slots.items():
        if str(key).endswith(suffix):
            return value
    return None


def _sync_game_variant_execution_plan(workflow: dict[str, Any], template_id: str) -> None:
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    template_id = str(template_id or spec.get("template_id") or "").strip()
    if template_id:
        spec["template_id"] = template_id
    spec["contract_schema_version"] = "game_variant_spec_v2"
    variant_parameters = spec.get("variant_parameters") if isinstance(spec.get("variant_parameters"), dict) else {}
    slot_bindings = spec.get("slot_bindings") if isinstance(spec.get("slot_bindings"), dict) else {}
    entity_application = spec.get("entity_application") if isinstance(spec.get("entity_application"), dict) else {}
    confirmation_gates = spec.get("confirmation_gates") if isinstance(spec.get("confirmation_gates"), list) else []
    capability_match = spec.get("template_capability_match") if isinstance(spec.get("template_capability_match"), dict) else {}
    spec["execution_plan"] = _build_patch_execution_plan(
        template_id=template_id,
        variant_parameters=variant_parameters,
        slot_bindings=slot_bindings,
        entity_application=entity_application,
        confirmation_gates=confirmation_gates,
        template_capability_match=capability_match,
    )
    render_spec = workflow.get("render_spec") if isinstance(workflow.get("render_spec"), dict) else {}
    if render_spec:
        execution = render_spec.setdefault("music_entity_execution", {})
        if isinstance(execution, dict):
            execution["contract_schema_version"] = spec["contract_schema_version"]
            execution["execution_plan"] = deepcopy(spec["execution_plan"])
            execution["variant_parameters"] = deepcopy(variant_parameters)
            execution["slot_bindings"] = deepcopy(slot_bindings)
            if entity_application:
                execution["entity_application"] = deepcopy(entity_application)


def _sync_frontend_execution_contract(workflow: dict[str, Any]) -> None:
    spec = workflow.get("game_variant_spec") if isinstance(workflow.get("game_variant_spec"), dict) else {}
    if not spec:
        return
    execution = _execution_contract_from_variant_spec(spec)
    render_spec = workflow.setdefault("render_spec", {})
    if isinstance(render_spec, dict):
        render_spec["music_entity_execution"] = deepcopy(execution)
    handoff = workflow.get("frontend_handoff_contract")
    if not isinstance(handoff, dict):
        return
    presentation_inputs = handoff.setdefault("presentation_inputs", {})
    if isinstance(presentation_inputs, dict):
        presentation_inputs["music_entity_execution"] = deepcopy(execution)
        presentation_inputs["template_capability_match"] = deepcopy(execution.get("template_capability_match", {}))


def _execution_contract_from_variant_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_schema_version": deepcopy(spec.get("contract_schema_version", "")),
        "music_entity": deepcopy(spec.get("music_entity", {})) if isinstance(spec.get("music_entity"), dict) else {},
        "variant_parameters": deepcopy(spec.get("variant_parameters", {})) if isinstance(spec.get("variant_parameters"), dict) else {},
        "slot_bindings": deepcopy(spec.get("slot_bindings", {})) if isinstance(spec.get("slot_bindings"), dict) else {},
        "entity_application": deepcopy(spec.get("entity_application", {})) if isinstance(spec.get("entity_application"), dict) else {},
        "material_entities": deepcopy(spec.get("material_entities", [])) if isinstance(spec.get("material_entities"), list) else [],
        "selected_entity": deepcopy(spec.get("selected_entity", {})) if isinstance(spec.get("selected_entity"), dict) else {},
        "template_capability_match": (
            deepcopy(spec.get("template_capability_match", {}))
            if isinstance(spec.get("template_capability_match"), dict)
            else {}
        ),
        "execution_plan": deepcopy(spec.get("execution_plan", {})) if isinstance(spec.get("execution_plan"), dict) else {},
        "confirmation_gates": deepcopy(spec.get("confirmation_gates", [])) if isinstance(spec.get("confirmation_gates"), list) else [],
        "teacher_confirmation_cards": deepcopy(spec.get("teacher_confirmation_cards", []))
        if isinstance(spec.get("teacher_confirmation_cards"), list)
        else [],
        "revision_history": deepcopy(spec.get("revision_history", [])) if isinstance(spec.get("revision_history"), list) else [],
    }


def _build_patch_execution_plan(
    *,
    template_id: str,
    variant_parameters: dict[str, Any],
    slot_bindings: dict[str, Any],
    entity_application: dict[str, Any],
    confirmation_gates: list[dict[str, Any]],
    template_capability_match: dict[str, Any],
) -> dict[str, Any]:
    blocked_reasons: list[str] = []
    if any(isinstance(gate, dict) and gate.get("status") != "confirmed" for gate in confirmation_gates):
        blocked_reasons.append("teacher_confirmation_required")
    if template_capability_match.get("status") == "rejected":
        blocked_reasons.append("template_capability_rejected")
    capability = template_capability_profile(template_id)
    writable_parameters = {str(item) for item in capability.get("writable_variant_parameters", [])}
    writable_slots = [str(item) for item in capability.get("writable_slot_bindings", [])]
    parameter_writes = [
        {"path": f"variant_parameters.{key}", "value": deepcopy(value)}
        for key, value in variant_parameters.items()
        if key in writable_parameters or key in _music_entity_authored_patch_parameters()
    ]
    slot_writes = [
        {"path": f"slot_bindings.{key}", "value": deepcopy(value)}
        for key, value in slot_bindings.items()
        if _slot_is_writable_for_patch(key, writable_slots)
    ]
    application_parameters = (
        entity_application.get("game_parameters")
        if isinstance(entity_application.get("game_parameters"), dict)
        else {}
    )
    application_slots = (
        entity_application.get("slot_bindings")
        if isinstance(entity_application.get("slot_bindings"), dict)
        else {}
    )
    return _drop_empty(
        {
            "version": "execution_plan_v1",
            "template_id": template_id,
            "status": "blocked" if blocked_reasons else "ready",
            "blocked_reasons": blocked_reasons,
            "entity_type": entity_application.get("entity_type", ""),
            "canonical_id": entity_application.get("canonical_id", ""),
            "parameter_writes": parameter_writes,
            "slot_writes": slot_writes,
            "entity_application_writes": {
                "game_parameters": deepcopy(application_parameters),
                "slot_bindings": deepcopy(application_slots),
            },
            "requires_teacher_confirmation": bool(blocked_reasons),
            "template_capability_status": template_capability_match.get("status", ""),
        }
    )


def _slot_is_writable_for_patch(slot: str, writable_slots: list[str]) -> bool:
    if slot in writable_slots:
        return True
    for pattern in writable_slots:
        if "*" not in pattern:
            continue
        prefix, _, suffix = pattern.partition("*")
        if slot.startswith(prefix) and slot.endswith(suffix):
            return True
    return False


def _music_entity_authored_patch_parameters() -> set[str]:
    return {
        "pattern_steps",
        "target_beats",
        "pitch_range",
        "target_solfege",
        "instrument_pool",
        "timbre_traits",
        "form_type",
        "melody_cards",
        "rhythm_cards",
        "required_elements",
    }


def _workflow_template_id(workflow: dict[str, Any], command: dict[str, Any]) -> str:
    instance = workflow.get("instance") if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    proposal = workflow.get("proposal_card") if isinstance(workflow.get("proposal_card"), dict) else {}
    return str(instance.get("template_id") or config.get("template_id") or proposal.get("template_id") or command.get("template_id") or "")


def _is_allowed_patch_path(path: str, capability: dict[str, Any]) -> bool:
    if not path.startswith("config."):
        return True
    key = path.split(".", 1)[1].split(".", 1)[0]
    allowed = {str(item) for item in capability.get("writable_variant_parameters", [])}
    return key in allowed


def _is_allowed_patch_value(path: str, value: Any, capability: dict[str, Any]) -> bool:
    if not path.startswith("config."):
        return True
    key = path.split(".", 1)[1].split(".", 1)[0]
    constraints = capability.get("variant_parameter_constraints")
    constraints = constraints if isinstance(constraints, dict) else {}
    constraint = constraints.get(key)
    if not isinstance(constraint, dict) or constraint.get("type") in {"", "any", None}:
        return True
    allowed_values = constraint.get("allowed_values") if isinstance(constraint.get("allowed_values"), list) else []
    constraint_type = str(constraint.get("type") or "")
    if constraint_type == "enum":
        return value in allowed_values
    if constraint_type in {"string", "enum_string"}:
        if not isinstance(value, str):
            return False
        return not allowed_values or value in allowed_values
    if constraint_type == "boolean":
        return isinstance(value, bool)
    if constraint_type == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        return _number_in_range(value, constraint)
    if constraint_type == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
        return _number_in_range(float(value), constraint)
    if constraint_type == "integer_list":
        if not isinstance(value, list) or not _list_size_in_range(value, constraint):
            return False
        item_min = constraint.get("item_min")
        item_max = constraint.get("item_max")
        for item in value:
            if not isinstance(item, int) or isinstance(item, bool):
                return False
            if isinstance(item_min, (int, float)) and item < item_min:
                return False
            if isinstance(item_max, (int, float)) and item > item_max:
                return False
        return True
    if constraint_type == "enum_list":
        return isinstance(value, list) and _list_size_in_range(value, constraint) and all(item in allowed_values for item in value)
    if constraint_type == "string_list":
        return isinstance(value, list) and _list_size_in_range(value, constraint) and all(isinstance(item, str) and item.strip() for item in value)
    return True


def _number_in_range(value: float, constraint: dict[str, Any]) -> bool:
    minimum = constraint.get("min")
    maximum = constraint.get("max")
    if isinstance(minimum, (int, float)) and value < minimum:
        return False
    if isinstance(maximum, (int, float)) and value > maximum:
        return False
    return True


def _list_size_in_range(value: list[Any], constraint: dict[str, Any]) -> bool:
    min_items = constraint.get("min_items")
    max_items = constraint.get("max_items")
    if isinstance(min_items, int) and len(value) < min_items:
        return False
    if isinstance(max_items, int) and len(value) > max_items:
        return False
    return True


def _record_patch_rejection_revision(
    workflow: dict[str, Any],
    command: dict[str, Any],
    rejected_paths: list[str],
    template_id: str,
) -> None:
    command_rejections = command.get("rejections") if isinstance(command.get("rejections"), list) else []
    if not command_rejections and not rejected_paths:
        return
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    history = spec.setdefault("revision_history", [])
    if not isinstance(history, list):
        spec["revision_history"] = history = []
    capability_check = command.get("capability_check") if isinstance(command.get("capability_check"), dict) else {}
    first_rejection = command_rejections[0] if command_rejections and isinstance(command_rejections[0], dict) else {}
    reason = str(first_rejection.get("reason") or ("unsupported_patch_paths_for_template" if rejected_paths else "patch_rejected"))
    recommended = str(first_rejection.get("recommended_template_id") or capability_check.get("recommended_template_id") or "")
    requested = str(first_rejection.get("requested_music_element") or capability_check.get("requested_music_element") or "")
    history.append(
        _drop_empty(
            {
                "revision_type": "patch_rejected",
                "template_id": template_id,
                "revision": command.get("revision", ""),
                "reason": reason,
                "rejected_paths": deepcopy(rejected_paths),
                "recommended_template_id": recommended,
                "requested_music_element": requested,
                "capability_check": deepcopy(capability_check),
                "teacher_message": _patch_rejection_teacher_message(template_id, requested, recommended, rejected_paths),
            }
        )
    )


def _patch_rejection_teacher_message(template_id: str, requested: str, recommended: str, rejected_paths: list[str]) -> str:
    if requested and recommended:
        return f"当前 {template_id} 模板不能处理{requested}，可改用 {recommended}。"
    if rejected_paths:
        return f"当前 {template_id} 模板不能修改这些字段：{', '.join(rejected_paths)}。"
    return f"当前 {template_id} 模板不能执行这次修改。"


def _patch_result(
    *,
    template_id: str,
    revision: str,
    operations: list[dict[str, Any]],
    rejections: list[dict[str, Any]],
    rejected_paths: list[str],
    entity_application: dict[str, Any],
) -> dict[str, Any]:
    first_rejection = rejections[0] if rejections and isinstance(rejections[0], dict) else {}
    requested = str(first_rejection.get("requested_music_element") or "").strip()
    recommended = str(first_rejection.get("recommended_template_id") or "").strip()
    if first_rejection:
        return {
            "status": "rejected",
            "teacher_message": _patch_rejection_teacher_message(template_id, requested, recommended, rejected_paths),
            "reason": str(first_rejection.get("reason") or "unsupported_music_element_for_template"),
            "recommended_template_id": recommended,
        }
    if rejected_paths and not operations:
        return {
            "status": "no_effect",
            "teacher_message": f"这次没有改到游戏，因为当前玩法不能修改这些内容：{', '.join(rejected_paths)}。",
            "reason": "all_patch_paths_rejected",
            "rejected_paths": deepcopy(rejected_paths),
        }
    applied = _applied_patch_summary(template_id, operations, entity_application)
    if applied:
        return {
            "status": "applied",
            "teacher_message": f"本次已改：{applied}",
            "applied_summary": applied,
        }
    provider_rejected = False
    if "重写" in revision or "全新网页" in revision:
        provider_rejected = True
    return {
        "status": "no_effect" if provider_rejected else "needs_clarification",
        "teacher_message": (
            "这次没有改到游戏，因为当前修改不能绕过模板重写网页。"
            if provider_rejected
            else "这次没有改到游戏：没有识别到可落到当前模板的具体修改。可以说明要改哪一关、哪种音乐材料、难度或提示方式。"
        ),
        "reason": "webpage_rewrite_forbidden" if provider_rejected else "no_template_patch_operation",
    }


def _applied_patch_summary(template_id: str, operations: list[dict[str, Any]], entity_application: dict[str, Any]) -> str:
    for operation in operations:
        if operation.get("op") == "round_patch":
            round_label = f"第 {operation.get('round')} 关"
            value_text = _value_label(operation.get("value"))
            if template_id == "rhythm_echo_core":
                return f"{round_label}节奏改为：{value_text}。"
            if template_id == "pitch_ladder_core":
                return f"{round_label}音高改为：{value_text}。"
            if template_id == "solfege_target_core":
                return f"{round_label}唱名改为：{value_text}。"
        if operation.get("op") == "form_segment_patch":
            return f"第 {operation.get('segment')} 段曲式改为：{operation.get('value')}。"
    params = entity_application.get("game_parameters") if isinstance(entity_application.get("game_parameters"), dict) else {}
    if template_id == "beat_guardian_core" and params.get("meter"):
        meter_label = "三拍子" if params.get("meter") == "3/4" else str(params.get("meter"))
        beats = _value_label(params.get("target_beats"))
        return f"节拍改为{meter_label}，目标拍位：{beats}。"
    if template_id == "rhythm_echo_core" and params.get("pattern_steps"):
        return f"节奏改为：{_value_label(params.get('pattern_steps'))}。"
    if template_id == "timbre_detective_core" and params.get("instrument_pool"):
        traits = params.get("timbre_traits")
        suffix = f"；听辨重点：{_value_label(traits)}" if traits else ""
        return f"音色对比改为：{_value_label(params.get('instrument_pool'))}{suffix}。"
    if template_id == "composition_puzzle_core" and params.get("melody_cards"):
        return f"创编素材改为：{_value_label(params.get('melody_cards'))}。"
    for operation in operations:
        if operation.get("op") == "set" and str(operation.get("path") or "").endswith(".difficulty"):
            return "难度已调低，更适合低年级或入门练习。"
        if operation.get("op") == "set" and str(operation.get("path") or "").endswith(".round_count"):
            return f"关卡数改为：{operation.get('value')}。"
    return ""


def _value_label(value: Any) -> str:
    labels = {
        "quarter": "四分",
        "rest": "休止",
        "eighth_pair": "八分八分",
        "syncopation": "切分",
        "dotted_quarter": "附点",
        "half": "二分",
    }
    if isinstance(value, list):
        return "、".join(labels.get(str(item), str(item)) for item in value)
    return labels.get(str(value), str(value))


def _is_locked_path(path: str, capability: dict[str, Any] | None = None) -> bool:
    locked = set(LOCKED_CONFIG_FIELDS)
    if isinstance(capability, dict):
        locked.update(str(item) for item in capability.get("locked_template_fields", []) if str(item))
    if path in locked:
        return True
    if path.startswith("config."):
        key = path.split(".", 1)[1].split(".", 1)[0]
        return key in locked or f"config.{key}" in locked
    key = path.split(".", 1)[-1]
    return key in locked


def _set_workflow_path(workflow: dict[str, Any], path: str, value: Any) -> None:
    if path.startswith("config."):
        target = workflow.setdefault("instance", {}).setdefault("config", {})
        parts = path.split(".")[1:]
    else:
        parts = path.split(".")
        target = workflow
    for part in parts[:-1]:
        if not isinstance(target.get(part), dict):
            target[part] = {}
        target = target[part]
    target[parts[-1]] = deepcopy(value)


def _target_scope(text: str) -> list[str]:
    scopes: list[str] = []
    round_no = _round_number_from_text(text)
    if round_no:
        scopes.append(f"round_{round_no}")
    segment_no = _segment_number_from_text(text)
    if segment_no:
        scopes.append(f"segment_{segment_no}")
    if any(token in text for token in ("节奏", "四分", "八分", "休止", "切分", "附点", "唱名", "音高", "do", "mi", "sol", "曲式", "段")):
        scopes.append("music_material")
    if any(token in text for token in ("三关", "两关", "四关", "五关", "关卡数")):
        scopes.append("round_count")
    return scopes or ["template_instance"]


def _round_number_from_text(text: str) -> int | None:
    digit_match = re.search(r"第\s*(\d+)\s*关", text)
    if digit_match:
        return int(digit_match.group(1))
    chinese_digits = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6}
    match = re.search(r"第\s*([一二两三四五六])\s*关", text)
    if match:
        return chinese_digits.get(match.group(1))
    return None


def _segment_number_from_text(text: str) -> int | None:
    digit_match = re.search(r"第\s*(\d+)\s*段", text)
    if digit_match:
        return int(digit_match.group(1))
    chinese_digits = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6}
    match = re.search(r"第\s*([一二两三四五六])\s*段", text)
    if match:
        return chinese_digits.get(match.group(1))
    return None


def _round_count_from_text(text: str) -> int | None:
    if not any(token in text for token in ("改成", "变成", "设置为", "关卡数", "总共", "一共", "只要", "只用")):
        return None
    digit_match = re.search(r"(?:改成|变成|设置为|关卡数|总共|一共|只要|只用)\s*(\d+)\s*关", text)
    if digit_match:
        return max(1, min(12, int(digit_match.group(1))))
    chinese_counts = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6}
    match = re.search(r"(?:改成|变成|设置为|关卡数|总共|一共|只要|只用)\s*([一二两三四五六])\s*关", text)
    if match:
        return chinese_counts.get(match.group(1))
    return None


def _intent_action_type(text: str, music_entity: dict[str, Any]) -> str:
    if music_entity.get("entity_type"):
        return "replace_music_entity"
    if _round_count_from_text(text) is not None or any(token in text for token in ("简单", "容易", "低年级", "太难")):
        return "adjust_difficulty"
    if any(token in text for token in ("按钮", "更大", "放大", "大一点", "皮肤", "风格", "颜色", "主题")):
        return "adjust_presentation"
    return "revise_template_instance"


def _intent_target(*, round_no: int | None, segment_no: int | None) -> dict[str, Any]:
    if round_no:
        return {"kind": "round", "round": round_no}
    if segment_no:
        return {"kind": "segment", "segment": segment_no}
    return {"kind": "template_instance"}


def _intent_difficulty(text: str) -> dict[str, Any]:
    if any(token in text for token in ("简单", "容易", "低年级", "太难", "第一关")):
        return {"level": "L1", "reason": "teacher_requested_easier_game"}
    count = _round_count_from_text(text)
    if count is not None:
        return {"round_count": count}
    return {}


def _intent_presentation(text: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    lowered = text.lower()
    if any(token in text for token in ("按钮", "更大", "放大", "大一点")) or "button" in lowered:
        payload["button_size"] = "large"
    if any(token in text for token in ("皮肤", "风格", "颜色", "更像", "主题")):
        payload["revision_note"] = text
    return payload


def _intent_music_entity(
    template_id: str,
    text: str,
    candidate: dict[str, Any],
    *,
    round_no: int | None,
    segment_no: int | None,
) -> dict[str, Any]:
    if template_id == "rhythm_echo_core":
        pattern = _rhythm_pattern_from_text(text)
        if pattern:
            return {"entity_type": "rhythm_pattern", "value": pattern}
    if template_id in {"pitch_ladder_core", "solfege_target_core"}:
        solfege = _solfege_from_text(text)
        if solfege:
            return {
                "entity_type": "pitch_motion" if template_id == "pitch_ladder_core" else "solfege_set",
                "value": solfege,
            }
    if template_id == "form_treasure_core":
        form_label = _form_label_from_text(text)
        if (segment_no or round_no) and form_label:
            return {"entity_type": "form_structure", "value": form_label}
    canonical = candidate.get("canonical_element") if isinstance(candidate.get("canonical_element"), dict) else {}
    entity = candidate.get("entity") if isinstance(candidate.get("entity"), dict) else {}
    entity_type = str(canonical.get("entity_type") or entity.get("kind") or "").strip()
    if entity_type == "timbre_set":
        return {
            "entity_type": "timbre_set",
            "value": {
                "instrument_pool": _string_list(entity.get("instrument_pool")),
                "timbre_traits": _string_list(entity.get("evidence_traits")),
                "comparison_pairs": deepcopy(entity.get("comparison_pairs") or []),
            },
        }
    if template_id == "beat_guardian_core" and entity_type == "meter":
        return {
            "entity_type": "meter",
            "value": {
                "meter": entity.get("meter", ""),
                "target_beats": deepcopy(entity.get("target_beats") or []),
                "accent_pattern": deepcopy(entity.get("accent_pattern") or []),
            },
        }
    if template_id == "composition_puzzle_core" and entity_type in {"scale", "composition_material"}:
        return {
            "entity_type": entity_type,
            "value": {
                "melody_cards": _string_list(entity.get("scale_degrees") or entity.get("melody_cards")),
                "required_elements": _string_list(entity.get("scale_degrees") or entity.get("melody_cards")),
            },
        }
    return {}


def _music_material_operations(template_id: str, text: str, config: dict[str, Any], *, round_no: int | None = None) -> list[dict[str, Any]]:
    if template_id == "rhythm_echo_core":
        pattern = _rhythm_pattern_from_text(text)
        if pattern:
            if round_no:
                return [
                    {
                        "op": "round_patch",
                        "round": round_no,
                        "field": "pattern_steps",
                        "value": pattern,
                    },
                    {"op": "set", "path": "config.round_count", "value": int(config.get("round_count") or 6)},
                ]
            return [{"op": "set", "path": "config.pattern_steps", "value": pattern}]
    if template_id in {"solfege_target_core", "pitch_ladder_core"}:
        solfege = _solfege_from_text(text)
        if solfege:
            field = "target_solfege" if template_id == "solfege_target_core" else "pitch_range"
            if round_no:
                round_field = "sequence"
                return [
                    {
                        "op": "round_patch",
                        "round": round_no,
                        "field": round_field,
                        "value": solfege,
                    }
                ]
            return [{"op": "set", "path": f"config.{field}", "value": solfege}]
    if template_id == "form_treasure_core":
        segment_no = _segment_number_from_text(text) or round_no
        form_label = _form_label_from_text(text)
        if segment_no and form_label:
            return [
                {
                    "op": "form_segment_patch",
                    "segment": segment_no,
                    "field": "form_label",
                    "value": form_label,
                }
            ]
        if "ABA" in text.upper():
            return [{"op": "set", "path": "config.form_type", "value": "ABA"}]
        if "回旋" in text:
            return [{"op": "set", "path": "config.form_type", "value": "回旋"}]
    return []


def _intent_entity_operations(template_id: str, intent: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    entity = intent.get("music_entity") if isinstance(intent.get("music_entity"), dict) else {}
    entity_type = str(entity.get("entity_type") or "").strip()
    value = entity.get("value")
    target = intent.get("target") if isinstance(intent.get("target"), dict) else {}
    try:
        round_no = int(target.get("round") or 0)
    except (TypeError, ValueError):
        round_no = 0
    operations: list[dict[str, Any]] = []

    if template_id == "rhythm_echo_core" and entity_type == "rhythm_pattern" and isinstance(value, list) and value:
        if round_no:
            operations.append({"op": "round_patch", "round": round_no, "field": "pattern_steps", "value": _string_list(value)})
            operations.append({"op": "set", "path": "config.round_count", "value": int(config.get("round_count") or 6)})
        else:
            operations.append({"op": "set", "path": "config.pattern_steps", "value": _string_list(value)})
    elif template_id == "pitch_ladder_core" and entity_type == "pitch_motion" and isinstance(value, list) and value:
        if round_no:
            operations.append({"op": "round_patch", "round": round_no, "field": "sequence", "value": _string_list(value)})
        else:
            operations.append({"op": "set", "path": "config.pitch_range", "value": _string_list(value)})
    elif template_id == "solfege_target_core" and entity_type == "solfege_set" and isinstance(value, list) and value:
        if round_no:
            operations.append({"op": "round_patch", "round": round_no, "field": "sequence", "value": _string_list(value)})
        else:
            operations.append({"op": "set", "path": "config.target_solfege", "value": _string_list(value)})
    elif template_id == "beat_guardian_core" and entity_type == "meter" and isinstance(value, dict):
        if value.get("meter"):
            operations.append({"op": "set", "path": "config.meter", "value": value.get("meter")})
        if isinstance(value.get("target_beats"), list) and value.get("target_beats"):
            operations.append({"op": "set", "path": "config.target_beats", "value": deepcopy(value.get("target_beats"))})
        if value.get("accent_pattern"):
            operations.append({"op": "set", "path": "config.mode", "value": "strong_beat_guard"})
    elif template_id == "timbre_detective_core" and entity_type == "timbre_set" and isinstance(value, dict):
        pool = _string_list(value.get("instrument_pool"))
        traits = _string_list(value.get("timbre_traits"))
        if pool:
            operations.append({"op": "set", "path": "config.instrument_pool", "value": pool[:6]})
        if traits:
            operations.append({"op": "set", "path": "config.timbre_traits", "value": traits[:7]})
        if pool or traits:
            operations.append({"op": "set", "path": "config.mode", "value": "compare_twins"})
    elif template_id == "composition_puzzle_core" and entity_type in {"scale", "composition_material"} and isinstance(value, dict):
        cards = _string_list(value.get("melody_cards") or value.get("required_elements"))
        if cards:
            operations.extend(
                [
                    {"op": "set", "path": "config.mode", "value": "melody_puzzle_creation"},
                    {"op": "set", "path": "config.melody_cards", "value": cards[:8]},
                    {"op": "set", "path": "config.required_elements", "value": cards[:8]},
                    {"op": "set", "path": "config.constraint_profile", "value": "guided"},
                ]
            )
    return _dedupe_operations(operations)


def _selected_entity_candidate(retrieval: dict[str, Any], template_id: str) -> dict[str, Any]:
    candidates = retrieval.get("candidates") if isinstance(retrieval.get("candidates"), list) else []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        match = candidate.get("template_match") if isinstance(candidate.get("template_match"), dict) else {}
        if str(match.get("template_id") or "").strip() == template_id:
            return deepcopy(candidate)
    return deepcopy(candidates[0]) if candidates and isinstance(candidates[0], dict) else {}


def _entity_grounded_operations(template_id: str, candidate: dict[str, Any], text: str) -> list[dict[str, Any]]:
    overrides = _entity_grounded_overrides(template_id, candidate, text)
    return [{"op": "set", "path": f"config.{key}", "value": value} for key, value in overrides.items()]


def _entity_grounded_overrides(template_id: str, candidate: dict[str, Any], text: str) -> dict[str, Any]:
    entity = candidate.get("entity") if isinstance(candidate.get("entity"), dict) else {}
    canonical = candidate.get("canonical_element") if isinstance(candidate.get("canonical_element"), dict) else {}
    if template_id == "beat_guardian_core" and canonical.get("entity_type") == "meter":
        overrides: dict[str, Any] = {}
        meter = str(entity.get("meter") or "").strip()
        if meter:
            overrides["meter"] = meter
        beats = entity.get("target_beats")
        if isinstance(beats, list) and beats:
            overrides["target_beats"] = deepcopy(beats)
        if any(token in text for token in ("强拍", "第一拍", "第1拍")):
            overrides["mode"] = "strong_beat_guard"
        return overrides
    if template_id == "timbre_detective_core" and canonical.get("entity_type") == "timbre_set":
        overrides = {}
        pool = _string_list(entity.get("instrument_pool"))
        traits = _string_list(entity.get("evidence_traits"))
        if len(pool) >= 2:
            overrides["instrument_pool"] = pool[:6]
        if traits:
            overrides["timbre_traits"] = traits[:7]
        if any(token in text for token in ("比较", "对比", "相似")):
            overrides["mode"] = "compare_twins"
        return overrides
    if template_id == "composition_puzzle_core" and canonical.get("entity_type") in {"scale", "composition_material"}:
        degrees = _string_list(entity.get("scale_degrees") or entity.get("melody_cards"))
        if degrees:
            return {
                "mode": "melody_puzzle_creation",
                "melody_cards": degrees[:8],
                "required_elements": degrees[:8],
                "constraint_profile": "guided",
            }
    return {}


def _entity_application(template_id: str, candidate: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    if not candidate:
        return {}
    canonical = candidate.get("canonical_element") if isinstance(candidate.get("canonical_element"), dict) else {}
    entity = candidate.get("entity") if isinstance(candidate.get("entity"), dict) else {}
    game_parameters = {
        str(operation.get("path", "")).removeprefix("config."): deepcopy(operation.get("value"))
        for operation in operations
        if operation.get("op") == "set" and str(operation.get("path") or "").startswith("config.")
    }
    slot_bindings: dict[str, Any] = {}
    round_rhythm_patches = [
        operation
        for operation in operations
        if operation.get("op") == "round_patch" and str(operation.get("field") or "") == "pattern_steps"
    ]
    round_sequence_patches = [
        operation
        for operation in operations
        if operation.get("op") == "round_patch" and str(operation.get("field") or "") == "sequence"
    ]
    if template_id == "beat_guardian_core":
        slot_bindings["meter.accent_pattern"] = deepcopy(entity.get("accent_pattern") or [])
        slot_bindings["meter.beat_count"] = entity.get("beat_count")
    elif template_id == "rhythm_echo_core":
        if round_rhythm_patches:
            for operation in round_rhythm_patches:
                round_no = int(operation.get("round") or 0)
                if round_no >= 1:
                    slot_bindings[f"round_{round_no}.target_rhythm"] = deepcopy(operation.get("value") or [])
        else:
            playback = entity.get("playback") if isinstance(entity.get("playback"), dict) else {}
            slot_bindings["rhythm.pattern_steps"] = deepcopy(playback.get("pattern_steps") or entity.get("answer_tokens") or [])
            slot_bindings["rhythm.duration_beats"] = deepcopy(entity.get("duration_beats") or [])
    elif template_id == "pitch_ladder_core":
        for operation in round_sequence_patches:
            round_no = int(operation.get("round") or 0)
            if round_no >= 1:
                slot_bindings[f"round_{round_no}.target_melody"] = deepcopy(operation.get("value") or [])
    elif template_id == "solfege_target_core":
        for operation in round_sequence_patches:
            round_no = int(operation.get("round") or 0)
            if round_no >= 1:
                slot_bindings[f"round_{round_no}.target_solfege"] = deepcopy(operation.get("value") or [])
    elif template_id == "timbre_detective_core":
        slot_bindings["timbre.comparison_pairs"] = deepcopy(entity.get("comparison_pairs") or [])
        slot_bindings["timbre.trait_targets"] = deepcopy(entity.get("trait_targets") or {})
    elif template_id == "form_treasure_core":
        slot_bindings["form.answer_pattern"] = deepcopy(entity.get("answer_pattern") or [])
        slot_bindings["form.timeline_segments"] = deepcopy(entity.get("timeline_segments") or [])
    elif template_id == "composition_puzzle_core":
        slot_bindings["composition.scale_degrees"] = deepcopy(entity.get("scale_degrees") or entity.get("melody_cards") or [])
        slot_bindings["composition.constraint_checks"] = deepcopy(entity.get("constraint_checks") or [])
    return _drop_empty(
        {
            "template_id": template_id,
            "canonical_id": canonical.get("id", ""),
            "entity_type": canonical.get("entity_type", ""),
            "label": canonical.get("label", ""),
            "game_parameters": game_parameters,
            "slot_bindings": slot_bindings,
            "requires_teacher_confirmation": False,
            "confirmation_status": "confirmed_by_teacher_revision",
            "rationale": candidate.get("rationale", ""),
        }
    )


def _intent_entity_application(template_id: str, intent: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    entity = intent.get("music_entity") if isinstance(intent.get("music_entity"), dict) else {}
    entity_type = str(entity.get("entity_type") or "").strip()
    if not entity_type:
        return {}
    value = entity.get("value")
    game_parameters = {
        str(operation.get("path", "")).removeprefix("config."): deepcopy(operation.get("value"))
        for operation in operations
        if operation.get("op") == "set" and str(operation.get("path") or "").startswith("config.")
    }
    slot_bindings: dict[str, Any] = {}
    for operation in operations:
        if operation.get("op") != "round_patch":
            continue
        round_no = int(operation.get("round") or 0)
        if round_no < 1:
            continue
        if template_id == "rhythm_echo_core" and operation.get("field") == "pattern_steps":
            slot_bindings[f"round_{round_no}.target_rhythm"] = deepcopy(operation.get("value") or [])
        elif template_id == "pitch_ladder_core" and operation.get("field") == "sequence":
            slot_bindings[f"round_{round_no}.target_melody"] = deepcopy(operation.get("value") or [])
        elif template_id == "solfege_target_core" and operation.get("field") == "sequence":
            slot_bindings[f"round_{round_no}.target_solfege"] = deepcopy(operation.get("value") or [])
    if template_id == "rhythm_echo_core" and entity_type == "rhythm_pattern" and isinstance(value, list) and not slot_bindings:
        slot_bindings["rhythm.pattern_steps"] = deepcopy(value)
    elif template_id == "beat_guardian_core" and entity_type == "meter" and isinstance(value, dict):
        slot_bindings["meter.accent_pattern"] = deepcopy(value.get("accent_pattern") or [])
        slot_bindings["meter.beat_count"] = len(value.get("accent_pattern") or []) or None
    elif template_id == "timbre_detective_core" and entity_type == "timbre_set" and isinstance(value, dict):
        slot_bindings["timbre.comparison_pairs"] = deepcopy(value.get("comparison_pairs") or [])
        slot_bindings["timbre.trait_targets"] = deepcopy(value.get("trait_targets") or {})
    return _drop_empty(
        {
            "template_id": template_id,
            "canonical_id": "dialog_intent",
            "entity_type": entity_type,
            "label": entity_type,
            "game_parameters": game_parameters,
            "slot_bindings": slot_bindings,
            "requires_teacher_confirmation": False,
            "confirmation_status": "confirmed_by_teacher_revision",
            "rationale": "自然语言修改意图已映射到当前模板可改项。",
        }
    )


def _dedupe_operations(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for operation in operations:
        key = (
            operation.get("op"),
            operation.get("path"),
            operation.get("round"),
            operation.get("field"),
            json.dumps(operation.get("value"), ensure_ascii=False, sort_keys=True),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(operation)
    return deduped


def _template_capability_check(template_id: str, text: str, candidate: dict[str, Any]) -> dict[str, Any]:
    capability = template_capability_profile(template_id)
    requested = _requested_music_element(text, candidate)
    if not requested:
        return {
            "status": "allowed",
            "template_id": template_id,
            "matched_music_element": "",
            "capability_version": capability.get("version", ""),
        }
    suitable = [str(item) for item in capability.get("suitable_music_elements", [])]
    unsuitable = [str(item) for item in capability.get("not_suitable_for", [])]
    supported = _matches_capability_term(requested, suitable)
    unsupported = _matches_capability_term(requested, unsuitable)
    if supported and not unsupported:
        return {
            "status": "allowed",
            "template_id": template_id,
            "matched_music_element": requested,
            "capability_version": capability.get("version", ""),
        }
    recommended = _recommended_template_for_music_element(requested)
    return {
        "status": "rejected",
        "template_id": template_id,
        "requested_music_element": requested,
        "recommended_template_id": recommended,
        "reason": f"{template_id} 不适合处理 {requested}，请使用 {recommended or '更匹配的模板'}。",
        "capability_version": capability.get("version", ""),
    }


def _requested_music_element(text: str, candidate: dict[str, Any]) -> str:
    explicit = [
        ("强弱拍", ("强弱拍", "强弱规律", "稳定拍", "拍号", "强拍", "弱拍", "二拍子", "三拍子", "四拍子", "第一拍", "第1拍")),
        ("音色听辨", ("音色", "笛子", "二胡", "乐器", "气息感", "弦鸣")),
        ("曲式结构排序", ("曲式", "ABA", "回旋", "段落排序")),
        ("节奏型", ("节奏", "四分", "八分", "休止", "切分", "附点", "ta", "ti")),
        ("音高路线", ("音高", "旋律走向", "级进", "跳进")),
        ("唱名", ("唱名", "do", "re", "mi", "sol", "la", "ti")),
        ("五声音阶", ("五声音阶", "宫商角徵羽")),
    ]
    for label, keywords in explicit:
        if any(keyword in text for keyword in keywords):
            return label
    return ""


def _matches_capability_term(requested: str, terms: list[str]) -> bool:
    requested_keys = _capability_keywords(requested)
    for term in terms:
        if requested == term or requested in term or term in requested:
            return True
        if requested_keys.intersection(_capability_keywords(term)):
            return True
    return False


def _capability_keywords(value: str) -> set[str]:
    keyword_groups = {
        "节奏": ("节奏", "时值", "四分", "八分", "休止", "切分", "附点"),
        "音高": ("音高", "旋律走向", "级进", "跳进"),
        "唱名": ("唱名", "do", "re", "mi", "sol", "la", "ti"),
        "音色": ("音色", "乐器", "笛子", "二胡", "气息感", "弦鸣"),
        "曲式": ("曲式", "ABA", "回旋", "段落", "重复对比"),
        "创编": ("创编", "五声音阶", "素材卡", "宫商角徵羽"),
        "节拍": ("节拍", "强弱拍", "强弱规律", "稳定拍", "拍号", "强拍", "弱拍", "二拍子", "三拍子", "四拍子", "第一拍", "第1拍"),
    }
    return {label for label, keywords in keyword_groups.items() if any(keyword in value for keyword in keywords)}


def _recommended_template_for_music_element(requested: str) -> str:
    for template_id in (
        "beat_guardian_core",
        "rhythm_echo_core",
        "pitch_ladder_core",
        "solfege_target_core",
        "timbre_detective_core",
        "form_treasure_core",
        "composition_puzzle_core",
    ):
        profile = template_capability_profile(template_id)
        if _matches_capability_term(requested, [str(item) for item in profile.get("suitable_music_elements", [])]):
            return template_id
    return ""


def _rhythm_pattern_from_text(text: str) -> list[str]:
    if not any(token in text for token in ("四分", "八分", "休止", "切分", "附点", "二分", "ta", "ti")):
        return []
    pattern: list[str] = []
    token_specs = [
        ("dotted_quarter", ("附点", "ta.")),
        ("syncopation", ("切分", "syncopation")),
        ("eighth_pair", ("八分八分", "八分", "ti-ti", "titi")),
        ("rest", ("休止", "空拍", "休")),
        ("half", ("二分", "ta-a")),
        ("quarter", ("四分", "ta")),
    ]
    normalized = text.replace("，", " ").replace("。", " ").replace(",", " ")
    chunks = [chunk for chunk in re.split(r"\s+", normalized) if chunk]
    for chunk in chunks:
        for token, keywords in token_specs:
            if any(keyword in chunk for keyword in keywords):
                pattern.append(token)
                break
    if pattern:
        return pattern
    for token, keywords in token_specs:
        if any(keyword in text for keyword in keywords):
            pattern.append(token)
    return pattern


def _solfege_from_text(text: str) -> list[str]:
    tokens = pitch_tokens_from_text(text)
    return tokens if len(tokens) >= 2 else []


def _form_label_from_text(text: str) -> str:
    normalized = text.upper()
    for label in ("A", "B", "C"):
        if re.search(rf"\b{label}\b", normalized) or f"{label}段" in normalized or f"{label} 段" in normalized:
            return label
    if "主题" in text or "再现" in text:
        return "A"
    if "对比" in text:
        return "B"
    if "新材料" in text or "新的材料" in text:
        return "C"
    return ""


def _sync_game_variant_spec(workflow: dict[str, Any], path: str, value: Any) -> None:
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    variant_parameters = spec.setdefault("variant_parameters", {})
    if not isinstance(variant_parameters, dict):
        spec["variant_parameters"] = variant_parameters = {}
    mapping = {
        "config.pattern_steps": "pattern_steps",
        "config.round_count": "round_count",
        "config.target_solfege": "target_solfege",
        "config.pitch_range": "pitch_range",
        "config.form_type": "form_type",
        "config.meter": "meter",
        "config.target_beats": "target_beats",
        "config.mode": "mode",
        "config.instrument_pool": "instrument_pool",
        "config.timbre_traits": "timbre_traits",
        "config.melody_cards": "melody_cards",
        "config.required_elements": "required_elements",
        "config.constraint_profile": "constraint_profile",
        "config.difficulty": "difficulty",
        "config.skin_id": "skin_id",
    }
    target_key = mapping.get(path)
    if target_key:
        variant_parameters[target_key] = deepcopy(value)


def _apply_round_patch(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    instance = workflow.setdefault("instance", {})
    config = instance.setdefault("config", {})
    template_id = str(instance.get("template_id") or config.get("template_id") or "")
    round_no = int(operation.get("round") or 0)
    if round_no < 1:
        return
    field = str(operation.get("field") or "").strip()
    value = deepcopy(operation.get("value"))
    if template_id == "pitch_ladder_core" and field == "sequence":
        _set_round_sequence(config, "pitch_rounds", round_no, value)
        return
    if template_id == "solfege_target_core" and field == "sequence":
        _set_round_sequence(config, "solfege_rounds", round_no, value)
        _set_round_sequence(config, "target_rounds", round_no, value)
        return
    round_patches = config.setdefault("round_patches", {})
    if not isinstance(round_patches, dict):
        config["round_patches"] = round_patches = {}
    round_key = f"round_{round_no}"
    patch = round_patches.setdefault(round_key, {})
    if not isinstance(patch, dict):
        round_patches[round_key] = patch = {}
    patch[field] = value
    scene_config = config.get("scene_config")
    if isinstance(scene_config, dict):
        scene_round_patches = scene_config.setdefault("round_patches", {})
        if isinstance(scene_round_patches, dict):
            scene_round_patches[round_key] = deepcopy(patch)


def _set_round_sequence(config: dict[str, Any], key: str, round_no: int, sequence: Any) -> None:
    rounds = config.get(key)
    if not isinstance(rounds, list) or round_no > len(rounds):
        return
    round_item = rounds[round_no - 1]
    if not isinstance(round_item, dict):
        return
    normalized = [str(item).strip() for item in sequence if str(item or "").strip()] if isinstance(sequence, list) else []
    if not normalized:
        return
    round_item["sequence"] = normalized
    round_item["labels"] = normalized[:]
    round_item["answer"] = normalized if len(normalized) > 1 else normalized[0]
    scene_config = config.get("scene_config")
    if isinstance(scene_config, dict) and isinstance(scene_config.get(key), list) and round_no <= len(scene_config[key]):
        scene_round = scene_config[key][round_no - 1]
        if isinstance(scene_round, dict):
            scene_round["sequence"] = normalized
            scene_round["labels"] = normalized[:]
            scene_round["answer"] = normalized if len(normalized) > 1 else normalized[0]


def _renormalize_template_instance_config(workflow: dict[str, Any]) -> None:
    instance = workflow.get("instance")
    if not isinstance(instance, dict):
        return
    config = instance.get("config")
    if not isinstance(config, dict):
        return
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if not template_id:
        return
    try:
        rebuilt = build_game_instance({**config, "template_id": template_id})
    except Exception:
        return
    rebuilt_config = rebuilt.get("config") if isinstance(rebuilt.get("config"), dict) else {}
    if not rebuilt_config:
        return
    preserved = {key: deepcopy(config[key]) for key in ("round_patches",) if key in config}
    instance["config"] = {**rebuilt_config, **preserved}
    if "round_patches" in preserved and isinstance(instance["config"].get("scene_config"), dict):
        instance["config"]["scene_config"]["round_patches"] = deepcopy(preserved["round_patches"])


def _apply_form_segment_patch(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    instance = workflow.setdefault("instance", {})
    config = instance.setdefault("config", {})
    template_id = str(instance.get("template_id") or config.get("template_id") or "")
    if template_id != "form_treasure_core" or operation.get("field") != "form_label":
        return
    segment_no = int(operation.get("segment") or 0)
    label = str(operation.get("value") or "").strip().upper()
    if segment_no < 1 or label not in {"A", "B", "C"}:
        return
    index = segment_no - 1
    answer_pattern = _normalized_answer_pattern(config.get("answer_pattern"))
    if index >= len(answer_pattern):
        return
    answer_pattern[index] = label
    config["answer_pattern"] = answer_pattern
    _sync_form_segments(config, index, label)
    _sync_form_structure_cards(config, answer_pattern)
    scene_config = config.get("scene_config")
    if isinstance(scene_config, dict):
        scene_config["answer_pattern"] = deepcopy(answer_pattern)
        _sync_form_segments(scene_config, index, label)
        _sync_form_structure_cards(scene_config, answer_pattern)


def _normalized_answer_pattern(value: Any) -> list[str]:
    if isinstance(value, list):
        pattern = [str(item or "").strip().upper() for item in value if str(item or "").strip()]
        pattern = [item for item in pattern if item in {"A", "B", "C"}]
        if len(pattern) >= 3:
            return pattern
    return ["A", "B", "A"]


def _sync_form_segments(config: dict[str, Any], index: int, label: str) -> None:
    segments = config.get("timeline_segments")
    if not isinstance(segments, list) or index >= len(segments):
        return
    segment = segments[index]
    if not isinstance(segment, dict):
        return
    segment["label"] = label
    segment["name"] = _form_segment_name(label)
    segment["midi_offsets"] = _form_segment_offsets(label)
    hint_mode = str(config.get("hint_mode") or "partial")
    segment["hint"] = _form_segment_hint(label, hint_mode)


def _sync_form_structure_cards(config: dict[str, Any], answer_pattern: list[str]) -> None:
    existing = config.get("structure_cards")
    cards = existing if isinstance(existing, list) else []
    by_label = {str(card.get("label") or "").upper(): card for card in cards if isinstance(card, dict)}
    labels = []
    for label in answer_pattern:
        if label not in labels:
            labels.append(label)
    normalized_cards = []
    hint_mode = str(config.get("hint_mode") or "partial")
    for label in labels:
        card = deepcopy(by_label.get(label, {}))
        card["id"] = str(card.get("id") or f"card-{label}")
        card["label"] = label
        card["name"] = str(card.get("name") or _form_segment_name(label))
        card["description"] = str(card.get("description") or _form_segment_hint(label, hint_mode))
        normalized_cards.append(card)
    config["structure_cards"] = normalized_cards


def _form_segment_name(label: str) -> str:
    return {"A": "主题段", "B": "对比段", "C": "新材料段"}.get(label, "段落")


def _form_segment_hint(label: str, hint_mode: str) -> str:
    if hint_mode == "challenge":
        return "只听音乐判断段落关系。"
    hints = {
        "A": "主题旋律会再次出现。",
        "B": "这里和主题形成对比。",
        "C": "这里出现新的材料。",
    }
    if hint_mode == "guided":
        return hints.get(label, "听它和前面是否相同。")
    return {"A": "像主题", "B": "有对比", "C": "新材料"}.get(label, "听关系")


def _form_segment_offsets(label: str) -> list[int]:
    return {
        "A": [0, 2, 4, 2],
        "B": [5, 4, 2, 0],
        "C": [7, 5, 4, 7],
    }.get(label, [0, 2, 4, 2])


def _sync_round_patch_to_variant_spec(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    slot_bindings = spec.setdefault("slot_bindings", {})
    if not isinstance(slot_bindings, dict):
        spec["slot_bindings"] = slot_bindings = {}
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "")
    round_no = int(operation.get("round") or 0)
    if round_no < 1:
        return
    field = str(operation.get("field") or "")
    value = deepcopy(operation.get("value"))
    if template_id == "rhythm_echo_core" and field == "pattern_steps":
        slot_bindings[f"round_{round_no}.target_rhythm"] = value
    elif template_id == "pitch_ladder_core" and field == "sequence":
        slot_bindings[f"round_{round_no}.target_melody"] = value
    elif template_id == "solfege_target_core" and field == "sequence":
        slot_bindings[f"round_{round_no}.target_solfege"] = value


def _sync_form_segment_patch_to_variant_spec(workflow: dict[str, Any], operation: dict[str, Any]) -> None:
    spec = workflow.setdefault("game_variant_spec", {})
    if not isinstance(spec, dict):
        workflow["game_variant_spec"] = spec = {}
    slot_bindings = spec.setdefault("slot_bindings", {})
    if not isinstance(slot_bindings, dict):
        spec["slot_bindings"] = slot_bindings = {}
    segment_no = int(operation.get("segment") or 0)
    label = str(operation.get("value") or "").strip().upper()
    if segment_no >= 1 and label:
        slot_bindings[f"segment_{segment_no}.form_label"] = label


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item or "").strip()]


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if value in ("", None, [], {}):
            continue
        result[key] = deepcopy(value)
    return result
