# 把某个活动需要的所有能力组合成完整工具包
from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activities.activity_registry import get_activity_template, list_activity_templates
from app.services.activities.adaptive_template_registry import adaptive_specs_for_activity
from app.services.activities.assessment_record_registry import assessment_record_specs_for_activity
from app.services.assets.asset_pack_template_registry import asset_pack_template_specs_for_activity
from app.services.games.component_library import get_component_spec
from app.services.activities.delivery_template_registry import delivery_templates_for_activity
from app.services.games.gameplay_template_catalog import gameplay_template_specs_for_activity
from app.services.materials.material_binding_registry import material_binder_specs_for_activity
from app.services.materials.material_entity_registry import material_entity_specs_for_activity
from app.services.activities.micro_activity_template_registry import micro_activity_specs_for_activity
from app.services.activities.scenario_template_registry import scenario_templates_for_activity
from app.services.instruments.teacher_control_registry import teacher_control_pack_ids_for_activity, teacher_control_specs_for_ids
from app.services.instruments.teaching_aid_registry import get_teaching_aid
from app.services.instruments.virtual_instrument_registry import get_virtual_instrument


def build_toolkit_spec(activity_id: str) -> dict[str, Any]:
    activity = get_activity_template(activity_id)
    toolkit = activity["toolkit"]
    components = [get_component_spec(component_id) for component_id in toolkit.get("components", [])]
    teaching_aids = [get_teaching_aid(aid_id) for aid_id in toolkit.get("teaching_aids", [])]
    virtual_instruments = [
        get_virtual_instrument(instrument_id)
        for instrument_id in toolkit.get("virtual_instruments", [])
    ]
    teacher_control_ids = teacher_control_pack_ids_for_activity(activity["teacher_controls"], activity["activity_id"])
    return {
        "version": "toolkit_spec_v1",
        "audience": "primary_school",
        "activity_id": activity["activity_id"],
        "activity_name": activity["name"],
        "selected": deepcopy(toolkit),
        "required_material_entities": deepcopy(activity["required_material_entities"]),
        "material_entity_specs": material_entity_specs_for_activity(activity["activity_id"]),
        "material_binder_specs": material_binder_specs_for_activity(activity["activity_id"]),
        "assessment_record_specs": assessment_record_specs_for_activity(activity["activity_id"]),
        "adaptive_template_specs": adaptive_specs_for_activity(activity["activity_id"]),
        "delivery_template_specs": delivery_templates_for_activity(activity["activity_id"]),
        "scenario_template_specs": scenario_templates_for_activity(activity["activity_id"]),
        "asset_pack_template_specs": asset_pack_template_specs_for_activity(activity["activity_id"]),
        "micro_activity_template_specs": micro_activity_specs_for_activity(activity["activity_id"]),
        "gameplay_template_specs": gameplay_template_specs_for_activity(activity["activity_id"]),
        "student_music_behaviors": deepcopy(activity["student_music_behaviors"]),
        "education_alignment": deepcopy(activity["education_alignment"]),
        "teacher_controls": deepcopy(activity["teacher_controls"]),
        "teacher_control_specs": teacher_control_specs_for_ids(teacher_control_ids),
        "component_specs": components,
        "teaching_aid_specs": teaching_aids,
        "virtual_instrument_specs": virtual_instruments,
        "why": _toolkit_reason(activity, teaching_aids, virtual_instruments),
    }


def list_toolkit_catalog() -> list[dict[str, Any]]:
    return [
        {
            "activity_id": activity["activity_id"],
            "activity_name": activity["name"],
            "grade_bands": deepcopy(activity["grade_bands"]),
            "student_music_behaviors": deepcopy(activity["student_music_behaviors"]),
            "education_alignment": deepcopy(activity["education_alignment"]),
            "selected": deepcopy(activity["toolkit"]),
            "material_entity_specs": material_entity_specs_for_activity(activity["activity_id"]),
            "component_specs": [
                get_component_spec(component_id)
                for component_id in activity["toolkit"].get("components", [])
            ],
            "material_binder_specs": material_binder_specs_for_activity(activity["activity_id"]),
            "assessment_record_specs": assessment_record_specs_for_activity(activity["activity_id"]),
            "adaptive_template_specs": adaptive_specs_for_activity(activity["activity_id"]),
            "delivery_template_specs": delivery_templates_for_activity(activity["activity_id"]),
            "scenario_template_specs": scenario_templates_for_activity(activity["activity_id"]),
            "asset_pack_template_specs": asset_pack_template_specs_for_activity(activity["activity_id"]),
            "micro_activity_template_specs": micro_activity_specs_for_activity(activity["activity_id"]),
            "gameplay_template_specs": gameplay_template_specs_for_activity(activity["activity_id"]),
            "teacher_control_specs": teacher_control_specs_for_ids(
                teacher_control_pack_ids_for_activity(activity["teacher_controls"], activity["activity_id"])
            ),
            "why": _toolkit_reason(
                activity,
                [get_teaching_aid(aid_id) for aid_id in activity["toolkit"].get("teaching_aids", [])],
                [
                    get_virtual_instrument(instrument_id)
                    for instrument_id in activity["toolkit"].get("virtual_instruments", [])
                ],
            ),
        }
        for activity in list_activity_templates()
    ]


def _toolkit_reason(
    activity: dict[str, Any],
    teaching_aids: list[dict[str, Any]],
    virtual_instruments: list[dict[str, Any]],
) -> str:
    aid_names = "、".join(aid["name"] for aid in teaching_aids) or "基础组件"
    instrument_names = "、".join(instrument["name"] for instrument in virtual_instruments) or "无需虚拟乐器"
    behaviors = "、".join(activity.get("student_music_behaviors", []))
    return (
        f"小学{activity['name']}优先让学生完成{behaviors}，"
        f"组合{aid_names}和{instrument_names}，教师可在课堂中调节。"
    )
