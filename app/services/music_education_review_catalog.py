from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activity_quality_gates import (
    evaluate_activity_library_quality,
    evaluate_game_template_music_logic_library_quality,
)
from app.services.activity_registry import list_activity_templates
from app.services.component_library import PRIMARY_COMPONENT_LIBRARY, list_component_library
from app.services.game_template_registry import list_game_templates
from app.services.material_binding_registry import list_material_binders
from app.services.music_practice_classification import (
    activity_practice_profile,
    component_practice_profile,
    material_binder_practice_profile,
    teaching_aid_practice_profile,
)
from app.services.teaching_aid_registry import list_teaching_aids
from app.services.virtual_instrument_catalog_v2 import (
    PERCUSSION_GRID_DEFINITION,
    get_audited_classroom_audio_asset,
    list_virtual_instruments_v2,
)


REVIEW_CATALOG_VERSION = "music_education_review_catalog_v1"
EXPECTED_COUNTS = {
    "component": 32,
    "activity": 32,
    "game": 7,
    "teaching_aid": 17,
    "virtual_instrument": 11,
    "material_binder": 9,
}

CLASSROOM_COMPONENT_ROUTES = {
    "song_audio_workbench": "/template-console/music-classroom-suite.html?component=song_audio_workbench",
    "score_audio_sync_player": "/template-console/music-classroom-suite.html?component=score_audio_sync_player",
    "ear_training_engine": "/template-console/music-classroom-suite.html?component=ear_training_engine",
    "vocal_choir_training": "/template-console/music-classroom-suite.html?component=vocal_choir_training",
    "ensemble_conductor": "/template-console/music-classroom-suite.html?component=ensemble_conductor",
}

ACTIVITY_REVIEW_ROUTES = {
    "rhythm_warmup": "/template-console/primary-activity-preview.html",
    "meter_body_movement": "/template-console/strong-weak-beat-preview.html",
    "steady_beat_walk": "/template-console/steady-beat-walk-preview.html",
    "phrase_singing_practice": "/template-console/phrase-singing-preview.html",
    "phrase_loop_singing": "/template-console/phrase-singing-preview.html",
    "lyrics_rhythm_practice": "/template-console/lyrics-rhythm-preview.html",
    "lyrics_rhythm_reading": "/template-console/lyrics-rhythm-preview.html",
    "rhythm_question_answer": "/template-console/rhythm-question-preview.html",
    "solfege_sorting": "/template-console/student-game.html?template=solfege_target_core&review=1",
    "solfege_echo_singing": "/template-console/solfege-echo-preview.html",
    "melody_contour_trace": "/template-console/melody-contour-preview.html",
    "simple_score_following": "/template-console/simple-score-preview.html",
    "picture_listening_intro": "/template-console/listening-choice-preview.html",
    "listen_choose_explain": "/template-console/listening-choice-preview.html",
    "lesson_opening_hook": "/template-console/lesson-opening-preview.html",
    "theme_return_action": "/template-console/theme-return-action-preview.html",
    "graphic_score_create": "/template-console/graphic-score-preview.html",
    "instrument_timbre_match": "/template-console/student-game.html?template=timbre_detective_core&review=1",
    "form_ordering": "/template-console/student-game.html?template=form_treasure_core&review=1",
    "instrument_family_sorting": "/template-console/instrument-family-preview.html",
    "body_percussion_builder": "/template-console/body-percussion-preview.html",
    "xylophone_creation": "/template-console/pentatonic-melody-preview.html",
    "orff_percussion_ensemble": "/template-console/orff-ensemble-preview.html",
    "classroom_band_roles": "/template-console/orff-ensemble-preview.html",
    "group_relay_performance": "/template-console/group-relay-preview.html",
    "show_and_peer_feedback": "/template-console/peer-feedback-preview.html",
    "exit_ticket_review": "/template-console/exit-ticket-preview.html",
    "song_audio_workbench_activity": CLASSROOM_COMPONENT_ROUTES["song_audio_workbench"],
    "score_audio_sync_practice": CLASSROOM_COMPONENT_ROUTES["score_audio_sync_player"],
    "ear_training_practice": CLASSROOM_COMPONENT_ROUTES["ear_training_engine"],
    "vocal_choir_training_activity": CLASSROOM_COMPONENT_ROUTES["vocal_choir_training"],
    "ensemble_conductor_rehearsal": CLASSROOM_COMPONENT_ROUTES["ensemble_conductor"],
}


def build_music_education_review_catalog() -> dict[str, Any]:
    categories = _build_categories()
    actual_counts = {category: len(items) for category, items in categories.items()}
    return {
        "version": REVIEW_CATALOG_VERSION,
        "actual_counts": actual_counts,
        "expected_counts": deepcopy(EXPECTED_COUNTS),
        "count_status": "pass" if actual_counts == EXPECTED_COUNTS else "fail",
        "activity_quality_report": evaluate_activity_library_quality(),
        "game_quality_report": evaluate_game_template_music_logic_library_quality(),
        "categories": categories,
    }


def build_music_education_review_preview(category: str, item_id: str) -> dict[str, Any]:
    items = _build_categories().get(str(category))
    if items is None:
        raise ValueError(f"unknown review category: {category}")
    item = next((candidate for candidate in items if candidate["id"] == item_id), None)
    if not item:
        raise ValueError(f"unknown review item: {category}/{item_id}")
    preview: dict[str, Any] = {
        "version": "music_education_review_preview_v1",
        "category": category,
        "item_id": item_id,
        "name": item["name"],
        "preview_kind": item["preview_kind"],
        "implementation_status": item["implementation_status"],
        "audit_example": True,
        "example_label": "审核示例",
        "full_screen_url": item.get("full_screen_url", ""),
        "professional_summary": {
            "purpose": item["purpose"],
            "music_elements": item["music_elements"],
            "student_actions": item["student_actions"],
            "teacher_focus": item["teacher_focus"],
        },
        "technical_details": deepcopy(item["technical_details"]),
    }
    if item.get("teaching_role"):
        preview["teaching_role"] = item["teaching_role"]
        preview["teaching_role_label"] = item["teaching_role_label"]
        preview["web_boundary"] = item["web_boundary"]
        preview["teacher_boundary"] = item["teacher_boundary"]
        preview["agent_default_allowed"] = item["agent_default_allowed"]
    if category == "activity":
        preview["flow"] = _activity_flow(item)
    elif category == "game":
        preview["flow"] = _game_flow(item)
        preview["resettable"] = True
    elif category == "material_binder":
        preview["binding_example"] = _binding_example(item)
    elif category == "component":
        preview["fixture"] = deepcopy(item["technical_details"].get("fixture", {}))
    elif category == "teaching_aid":
        preview["classroom_preview"] = {
            "replaces": item["technical_details"].get("replace_physical_aid", ""),
            "components": item["technical_details"].get("components", []),
        }
    elif category == "virtual_instrument":
        preview["audio_preview"] = {
            "audited": bool(item["technical_details"].get("audited_audio")),
            "source": item["technical_details"].get("audited_audio", {}).get("sourceUrl", ""),
            "license": item["technical_details"].get("audited_audio", {}).get("licenseId", ""),
            "attribution": item["technical_details"].get("audited_audio", {}).get("attribution", ""),
            "requires_combined_audio": bool(item["technical_details"].get("requires_audited_audio_and_image")),
        }
    return preview


def _build_categories() -> dict[str, list[dict[str, Any]]]:
    return {
        "component": [
            _component_item(spec)
            for spec in list_component_library()
            if str(spec.get("component_id") or "") in PRIMARY_COMPONENT_LIBRARY
        ],
        "activity": [_activity_item(spec) for spec in list_activity_templates()],
        "game": [_game_item(spec) for spec in list_game_templates()],
        "teaching_aid": [_teaching_aid_item(spec) for spec in list_teaching_aids() if not spec.get("legacy_alias")],
        "virtual_instrument": [
            *[_virtual_instrument_item(spec) for spec in list_virtual_instruments_v2()],
            _virtual_instrument_item(PERCUSSION_GRID_DEFINITION),
        ],
        "material_binder": [_material_binder_item(spec) for spec in list_material_binders()],
    }


def _base_item(**values: Any) -> dict[str, Any]:
    lifecycle_status = values.pop("lifecycle_status", None)
    payload = dict(values)
    if lifecycle_status:
        payload["lifecycle_status"] = lifecycle_status
    return payload


def _teaching_role_fields(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "teaching_role": str(profile["role"]),
        "teaching_role_label": str(profile["label"]),
        "web_boundary": str(profile["web_boundary"]),
        "teacher_boundary": str(profile["teacher_boundary"]),
        "agent_default_allowed": bool(profile["agent_default_allowed"]),
    }


def _component_item(spec: dict[str, Any]) -> dict[str, Any]:
    item_id = str(spec["component_id"])
    practice_profile = component_practice_profile(item_id)
    official = item_id in PRIMARY_COMPONENT_LIBRARY
    focus = _strings(spec.get("education_notes")) or _strings(spec.get("behaviors"))
    if not official:
        focus = ["旧版兼容项：禁止智能体优先调用。", *focus]
    full_screen_url = CLASSROOM_COMPONENT_ROUTES.get(item_id, "")
    return _base_item(
        id=item_id,
        name=str(spec.get("name") or item_id),
        category="component",
        purpose=str(spec.get("purpose") or "用于组合音乐课堂活动。"),
        music_elements=_strings(spec.get("music_elements")) or _strings(spec.get("layers")),
        student_actions=_strings(spec.get("student_actions")) or _strings(spec.get("behaviors")),
        teacher_focus=focus or _strings(spec.get("quality_gates")),
        implementation_status="live" if full_screen_url else "preview_ready",
        preview_kind="live_component" if full_screen_url else "component_fixture",
        lifecycle_status="official" if official else "compatibility",
        full_screen_url=full_screen_url,
        **_teaching_role_fields(practice_profile),
        technical_details={
            "role": spec.get("role", ""),
            "runtime": spec.get("runtime", ""),
            "required_material_entities": spec.get("required_material_entities", []),
            "teacher_controls": spec.get("teacher_controls", []),
            "required_elements": spec.get("required_elements", []),
            "quality_gates": spec.get("quality_gates", []),
            "fixture": spec.get("fixture", {}),
        },
    )


def _activity_item(spec: dict[str, Any]) -> dict[str, Any]:
    alignment = spec.get("education_alignment") if isinstance(spec.get("education_alignment"), dict) else {}
    item_id = str(spec["activity_id"])
    practice_profile = activity_practice_profile(item_id)
    route = ACTIVITY_REVIEW_ROUTES.get(item_id, "")
    return _base_item(
        id=item_id,
        name=str(spec.get("name") or item_id),
        category="activity",
        purpose=_activity_purpose(alignment),
        music_elements=_strings(alignment.get("music_elements")),
        student_actions=_strings(spec.get("student_music_behaviors")),
        teacher_focus=_strings(alignment.get("pedagogy_notes")) or _strings(spec.get("acceptance")),
        implementation_status="live" if route else "contract_only",
        preview_kind="activity_runtime" if route else "activity_contract",
        full_screen_url=route,
        **_teaching_role_fields(practice_profile),
        technical_details={
            "grade_bands": spec.get("grade_bands", []),
            "classroom_stage": spec.get("classroom_stage", []),
            "required_material_entities": spec.get("required_material_entities", []),
            "teacher_controls": spec.get("teacher_controls", []),
            "acceptance": spec.get("acceptance", []),
            "toolkit": spec.get("toolkit", {}),
            "music_learning_path": alignment.get("music_learning_path", {}),
        },
    )


def _game_item(spec: dict[str, Any]) -> dict[str, Any]:
    item_id = str(spec["template_id"])
    config = spec.get("default_config") if isinstance(spec.get("default_config"), dict) else {}
    return _base_item(
        id=item_id,
        name=str(spec.get("label") or item_id),
        category="game",
        purpose=str(spec.get("description") or "用音乐任务、回合和反馈组成完整游戏。"),
        music_elements=_strings(spec.get("learning_targets")),
        student_actions=_strings(spec.get("student_actions")),
        teacher_focus=[str(config.get("teacher_prompt") or "检查游戏是否回到音乐目标。")],
        implementation_status="live",
        preview_kind="game_runtime",
        full_screen_url=f"/template-console/student-game.html?template={item_id}&review=1",
        technical_details={
            "family": spec.get("family", ""),
            "runtime_status": spec.get("runtime_status", spec.get("status", "")),
            "core_loop": spec.get("core_loop", []),
            "supported_modes": spec.get("supported_modes", []),
            "difficulty_axes": spec.get("difficulty_axes", []),
            "default_config": config,
        },
    )


def _teaching_aid_item(spec: dict[str, Any]) -> dict[str, Any]:
    item_id = str(spec["aid_id"])
    practice_profile = teaching_aid_practice_profile(item_id)
    compatibility = bool(spec.get("legacy_alias"))
    runtime = spec.get("runtime") if isinstance(spec.get("runtime"), dict) else {}
    supported_activity_ids = _strings(runtime.get("supported_activity_ids"))
    classroom_activity_id = next((activity_id for activity_id in supported_activity_ids if activity_id in ACTIVITY_REVIEW_ROUTES), "")
    classroom_activity_url = ACTIVITY_REVIEW_ROUTES.get(classroom_activity_id, "")
    return _base_item(
        id=item_id,
        name=str(spec.get("name") or item_id),
        category="teaching_aid",
        purpose=f"在网页中替代{spec.get('replace_physical_aid') or '实体音乐教具'}。",
        music_elements=_strings(spec.get("material_entities")),
        student_actions=_strings(spec.get("student_actions")),
        teacher_focus=_strings(spec.get("quality_gates")),
        implementation_status="preview_ready",
        preview_kind="teaching_aid_preview",
        lifecycle_status="compatibility" if compatibility else "official",
        full_screen_url=classroom_activity_url,
        **_teaching_role_fields(practice_profile),
        technical_details={
            "classroom_activity_id": classroom_activity_id,
            "replace_physical_aid": spec.get("replace_physical_aid", ""),
            "components": spec.get("components", []),
            "teacher_controls": spec.get("teacher_controls", []),
            "quality_gates": spec.get("quality_gates", []),
            "asset_policy": spec.get("asset_policy", {}),
            "runtime": spec.get("runtime", {}),
        },
    )


def _virtual_instrument_item(spec: dict[str, Any]) -> dict[str, Any]:
    item_id = str(spec["id"])
    is_grid = item_id == "virtual_percussion_grid"
    audio_asset = None if is_grid else get_audited_classroom_audio_asset(item_id)
    family = str(spec.get("family") or "percussion")
    zones = spec.get("zones") if isinstance(spec.get("zones"), list) else []
    pitch_range = spec.get("pitchRange") if isinstance(spec.get("pitchRange"), dict) else {}
    teacher_focus = [
        "审核演奏界面、可触区域和声音反馈是否与乐器类别一致。",
        "只允许使用已审核音频和皮肤资源，不能以空白面板或通用声音冒充乐器。",
    ]
    if is_grid:
        teacher_focus.append("六宫格由教师选择2至6件已审核打击乐器及其击打区域。")
    elif audio_asset:
        teacher_focus.append(f"音频来源已审核：{audio_asset.get('licenseId', '')}。发布时保留署名与许可。")
    return _base_item(
        id=item_id,
        name=str(spec.get("name") or item_id),
        category="virtual_instrument",
        purpose="让学生在已审核的真实演奏界面中听、奏和记录。" if not is_grid else "让教师组合已审核打击乐器，学生在六宫格中完成课堂节奏演奏。",
        music_elements=["音色", "演奏", family],
        student_actions=["听", "奏", "记录"],
        teacher_focus=teacher_focus,
        implementation_status="live",
        preview_kind="virtual_instrument_runtime",
        full_screen_url=f"/template-console/virtual-instrument-review.html?instrument={item_id}",
        technical_details={
            "family": family,
            "layout": spec.get("layout", "grid"),
            "layout_modes": spec.get("layoutModes", []),
            "pitch_range": pitch_range,
            "zones": zones,
            "supports_multi_touch": spec.get("supportsMultiTouch", False),
            "supports_recording": spec.get("supportsRecording", False),
            "skin": spec.get("skin", {}),
            "audited_audio": audio_asset or {},
            "requires_audited_audio_and_image": bool(spec.get("requiresAuditedAudioAndImage")),
        },
    )


def _material_binder_item(spec: dict[str, Any]) -> dict[str, Any]:
    item_id = str(spec["binder_id"])
    practice_profile = material_binder_practice_profile(item_id)
    return _base_item(
        id=item_id,
        name=str(spec.get("label") or item_id),
        category="material_binder",
        purpose=str(spec.get("music_education_use") or "把教师材料绑定到可调用组件。"),
        music_elements=[str(spec.get("primary_material_kind") or "音乐材料")],
        student_actions=_strings(spec.get("student_music_practices")),
        teacher_focus=_strings(spec.get("quality_gates")),
        implementation_status="preview_ready",
        preview_kind="binding_example",
        full_screen_url="",
        **_teaching_role_fields(practice_profile),
        technical_details={
            "primary_material_kind": spec.get("primary_material_kind", ""),
            "input_entities": spec.get("input_entities", []),
            "output_entities": spec.get("output_entities", []),
            "applicable_activity_ids": spec.get("applicable_activity_ids", []),
            "quality_gates": spec.get("quality_gates", []),
        },
    )


def _activity_flow(item: dict[str, Any]) -> list[dict[str, str]]:
    actions = "、".join(item["student_actions"]) or "完成音乐任务"
    focus = item["teacher_focus"][0] if item["teacher_focus"] else "教师确认音乐表现。"
    return [
        {"id": "listen", "label": "听", "description": f"先听清{'、'.join(item['music_elements']) or '本轮音乐材料'}。"},
        {"id": "do", "label": "做", "description": f"学生{actions}。"},
        {"id": "feedback", "label": "反馈", "description": "网页呈现可客观记录的操作证据。"},
        {"id": "teacher_confirm", "label": "教师确认", "description": focus},
    ]


def _game_flow(item: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"id": f"step_{index + 1}", "label": step, "description": f"审核游戏循环第 {index + 1} 步。"}
        for index, step in enumerate(_strings(item["technical_details"].get("core_loop")))
    ]


def _binding_example(item: dict[str, Any]) -> dict[str, Any]:
    inputs = _strings(item["technical_details"].get("input_entities"))
    outputs = _strings(item["technical_details"].get("output_entities"))
    activities = _strings(item["technical_details"].get("applicable_activity_ids"))
    return {
        "source": {name: _example_value(name) for name in inputs},
        "structured_result": {name: f"已从审核示例生成 {name}" for name in outputs},
        "component_targets": activities or ["待教师选择的课堂活动"],
    }


def _example_value(name: str) -> Any:
    values = {
        "song_title": "审核示例歌曲",
        "lyrics_phrase": "审核示例乐句",
        "lyrics_text": "审核示例歌词",
        "melody_phrase": ["do", "re", "mi", "sol"],
        "audio_clip": "/static/review/example-audio.wav",
        "rhythm_pattern": ["quarter", "eighth_pair", "quarter"],
        "meter": "2/4",
        "solfege_set": ["do", "re", "mi", "sol", "la"],
        "classroom_group_task": {"groups": 2, "goal": "轮流进入并合作倾听"},
    }
    return deepcopy(values.get(name, f"审核示例：{name}"))


def _activity_purpose(alignment: dict[str, Any]) -> str:
    path = alignment.get("music_learning_path") if isinstance(alignment.get("music_learning_path"), dict) else {}
    return str(path.get("experience") or next(iter(_strings(alignment.get("pedagogy_notes"))), "用于小学音乐课堂实践。"))


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]
