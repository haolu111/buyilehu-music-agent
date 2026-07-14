from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.animation_plan_builder import build_animation_plan
from app.services.asset_contract_builder import build_asset_contract
from app.services.audio_manifest_builder import build_audio_manifest
from app.services.game_feel_qa import build_game_feel_qa_report
from app.services.game_mechanic_contract import build_game_design
from app.services.level_curve_builder import build_level_curve
from app.services.music_game_production_spec import assemble_music_game_production_spec, build_game_concept_from_segment_brief
from app.services.music_truth_builder import build_music_truth
from app.services.original_game_production_builder import (
    build_component_assembly_plan,
    build_game_state_machine,
    build_generated_asset_registry,
    build_image_generation_tasks,
    build_lesson_runtime_generated_assets,
    build_original_game_concept,
)


def build_music_game_production_spec(
    *,
    workflow_kind: str,
    activity_spec: dict[str, Any],
    source: dict[str, Any],
    instance: dict[str, Any],
    game_variant_spec: dict[str, Any] | None = None,
    segment_game_brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the internal MusicGameSkill pipeline and return one production package."""

    game_variant_spec = game_variant_spec if isinstance(game_variant_spec, dict) else {}
    segment_game_brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    if segment_game_brief:
        instance = deepcopy(instance)
        config = dict(instance.get("config", {})) if isinstance(instance.get("config"), dict) else {}
        config["lesson_specific_assets_required"] = True
        config.setdefault("lesson_material", segment_game_brief.get("source_evidence") or "")
        config.setdefault("music_concept", segment_game_brief.get("music_learning_target") or "")
        config.setdefault("theme", segment_game_brief.get("core_mechanic") or config.get("theme") or "")
        instance["config"] = config
    game_concept = build_game_concept_from_segment_brief(segment_game_brief)
    if game_concept:
        activity_spec = {**activity_spec, "source_segment_id": game_concept.get("source_segment_id", "")}
    game_design = build_game_design(instance, activity_spec=activity_spec)
    music_truth = build_music_truth(
        instance,
        source=source,
        game_variant_spec=game_variant_spec,
        segment_game_brief=segment_game_brief,
    )
    audio_manifest = build_audio_manifest(instance, music_truth=music_truth)
    level_curve = build_level_curve(instance, music_truth=music_truth)
    scene_bible = _scene_bible_for(instance, game_design=game_design)
    asset_contract = build_asset_contract(instance, scene_bible=scene_bible)
    original_game_concept = build_original_game_concept(
        instance,
        game_concept=game_concept,
        segment_game_brief=segment_game_brief,
    )
    component_assembly_plan = build_component_assembly_plan(
        instance,
        game_design=game_design,
        original_game_concept=original_game_concept,
    )
    game_state_machine = build_game_state_machine(
        instance,
        game_design=game_design,
        level_curve=level_curve,
        asset_contract=asset_contract,
    )
    lesson_runtime_generated_assets = build_lesson_runtime_generated_assets(
        instance,
        asset_contract=asset_contract,
        segment_game_brief=segment_game_brief,
        original_game_concept=original_game_concept,
    )
    image_generation_tasks = build_image_generation_tasks(
        instance,
        asset_contract=asset_contract,
        scene_bible=scene_bible,
        lesson_runtime_generated_assets=lesson_runtime_generated_assets,
    )
    generated_asset_registry = build_generated_asset_registry(
        instance,
        asset_contract=asset_contract,
        image_generation_tasks=image_generation_tasks,
    )
    animation_plan = build_animation_plan(instance)
    return assemble_music_game_production_spec(
        workflow_kind=workflow_kind,
        activity_spec=activity_spec,
        source=source,
        instance=instance,
        game_design=game_design,
        music_truth=music_truth,
        audio_manifest=audio_manifest,
        level_curve=level_curve,
        scene_bible=scene_bible,
        asset_contract=asset_contract,
        original_game_concept=original_game_concept,
        component_assembly_plan=component_assembly_plan,
        game_state_machine=game_state_machine,
        image_generation_tasks=image_generation_tasks,
        generated_asset_registry=generated_asset_registry,
        lesson_runtime_generated_assets=lesson_runtime_generated_assets,
        animation_plan=animation_plan,
        game_concept=game_concept,
        qa_builder=build_game_feel_qa_report,
    )


def _scene_bible_for(instance: dict[str, Any], *, game_design: dict[str, Any]) -> str:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if config.get("lesson_specific_assets_required"):
        title = str(config.get("lesson_title") or "当前课例")
        target = str(config.get("music_concept") or "音乐学习目标")
        material = str(config.get("lesson_material") or "教案音乐材料")
        scene = str(config.get("lesson_scene_context") or "明亮小学音乐课堂，中央留出学生操作区域。")
        role = str(config.get("lesson_role_visual") or config.get("cartoon_role") or "音乐引导角色")
        prop = str(config.get("lesson_prop_visual") or "音乐任务道具")
        classroom_return = str(config.get("teacher_prompt") or config.get("result_transfer_prompt") or "回到课堂音乐材料再次表现。")
        return "\n".join(
            [
                "# scene-bible",
                "",
                f"课例来源：《{title}》。",
                f"教学环节：{material} 的课堂音乐游戏化练习。",
                f"音乐学习目标：{target}。",
                "学生操作行为：听音乐材料，预判音乐目标，同步点击或拍击，并根据早晚/漏拍反馈调整。",
                f"游戏情境一句话：{scene}",
                f"主场景：{scene} 下方 25% 留给拍点轨道、操作按钮和教师投屏信息。",
                f"主角色：{role}，圆润、低年级友好，面向操作区。",
                f"道具和音乐意义：{prop} 代表学生要操作的音乐目标，不能只是装饰。",
                "角色姿势状态：idle、listen、ready、action、success、fail、retry、reward 都要能表达游戏状态。",
                "色彩和画风：明亮、儿童友好、课堂可投屏，避免高复杂度背景。",
                "UI 留白区域：中央保留互动区，下方保留拍点轨道和按钮，右侧可放奖励反馈。",
                "禁止元素：文字、logo、水印、版权角色、恐怖雨夜、遮挡操作区、和音乐任务无关的复杂物件。",
                f"课堂回扣方式：{classroom_return}",
                "资产需求：背景图、人物姿势图、道具图、奖励图和反馈图必须进入运行时资产登记。",
            ]
        )
    if template_id == "rhythm_echo_core":
        return "\n".join(
            [
                "# scene-bible",
                "",
                "模板：节奏复刻。",
                f"主题：{config.get('theme') or '节奏电波'}。",
                f"角色：{config.get('cartoon_role') or '节奏引导员'}。",
                "课堂情境：学生在音乐课堂中跟随真实节奏信号，完成听辨、记忆、复刻和课堂回扣。",
                "画面原则：低年级一眼看到听、拍、反馈，不让装饰遮挡节奏轨道。",
                f"核心操作：{game_design.get('mechanic_contract', {}).get('student_action', '')}",
                "资产需求：背景图、角色 idle/action/success/fail 姿势、节奏道具、奖励与错误反馈图。",
                "禁止元素：恐怖、暴力、复杂文字说明、遮挡拍点的装饰。",
            ]
        )
    return "\n".join(
        [
            "# scene-bible",
            "",
            f"模板：{template_id}。",
            "课堂情境：围绕当前教案音乐目标生成可上课的游戏场景。",
            "画面必须服务课堂音乐任务，角色、道具和 UI 风格保持一致。",
            "资产需求：背景图、人物姿势图、道具图、奖励图和反馈图必须进入运行时资产登记。",
        ]
    )
