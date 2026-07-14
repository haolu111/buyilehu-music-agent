from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.asset_pack_file_validator import asset_pack_file_report
from app.services.asset_pack_registry import get_asset_pack, list_asset_packs


REQUIRED_ASSET_PACK_TEMPLATE_FIELDS = (
    "version",
    "asset_pack_template_id",
    "linked_manifest_id",
    "label",
    "audience",
    "source_kind",
    "included_assets",
    "usage",
    "generation_requirement",
    "authenticity_policy",
    "applicable_activity_ids",
    "supports_teaching_aids",
    "supports_virtual_instruments",
    "supports_ensemble_controllers",
    "music_elements",
    "student_music_practices",
    "classroom_role",
    "quality_gates",
)


TEMPLATE_OVERRIDES: dict[str, dict[str, Any]] = {
    "primary_instrument_card_pack": {
        "classroom_role": "替代实体乐器图卡，用于先听音色、再辨认乐器、再进入分类或合奏分工。",
        "authenticity_policy": "必须使用真实、可追溯、开源或公有领域乐器照片；不能用生成插图冒充真实乐器照片。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "open_license_sources",
            "save_policy": "真实照片已保存到 manifest 指定路径，后续新增乐器必须补 source_url、license、attribution。",
        },
        "quality_gates": [
            "真实照片来源可追溯",
            "每张乐器卡必须绑定音色或发声方式任务",
            "不得把生成插图标为真实照片",
            "本地文件存在且 license/attribution 可查",
        ],
    },
    "generated_playable_instrument_pack": {
        "classroom_role": "替代小学课堂可演奏乐器皮肤和实体乐器操作界面，用于先听采样、再演奏、分类、合奏或创编。",
        "authenticity_policy": "这是本地生图器 image2 模型生成的库乐队式演奏界面皮肤，不声明为真实照片；学生可点击演奏，但真实感由采样音频合同保证。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "image2",
            "save_policy": "模板库固定乐器皮肤统一用本地生图器 image2 模型逐个生成 PNG，并保存到 generated_playable_instrument_pack/images；后续新增乐器必须先生成独立 PNG，再进入 ready 列表。",
        },
        "quality_gates": [
            "generated_instrument_skin_visible",
            "real_sample_playback",
            "no_web_photo_fallback",
            "one_playable_instrument_one_skin",
            "ensemble_controller_must_not_be_used_as_playable_skin",
            "缺图必须显示 pending_generated_skin",
            "生成图不得声明为真实照片",
        ],
    },
    "music_mood_picture_pack": {
        "classroom_role": "替代实体情绪图卡，用于听赏初听后的情绪选择和音乐依据表达。",
        "authenticity_policy": "使用本地生图器 image2 模型生成的非写实情绪图卡，但不能代替真实乐器照片；图像只辅助表达，不能替代聆听。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "image_gen",
            "save_policy": "生成 PNG 已保存到 manifest 指定路径；后续重生成仍需通过 PNG 文件校验。字段名保留兼容旧 manifest，本次新增模板库资产使用 codex2api/image2 生成。",
        },
        "quality_gates": [
            "生成 PNG 文件验收通过",
            "情绪图近似正方形且无文字水印",
            "学生选择图片后必须说出速度、力度、音色或旋律依据",
            "mood_symbol_card_pack 只作为低保 fallback，不能替代正式 image_gen PNG 入库",
        ],
    },
    "mood_symbol_card_pack": {
        "classroom_role": "作为听赏情绪图卡的项目生成 fallback，保证 image_gen PNG 不可用时课堂仍可演示。",
        "authenticity_policy": "这是符号化图卡，不声明为 image_gen 生成结果，也不声明为真实照片。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "project_generated_svg",
            "save_policy": "SVG fallback 已在项目内生成；正式情绪图仍以 music_mood_picture_pack 的 image_gen PNG 为准。",
        },
        "quality_gates": [
            "fallback 文件存在",
            "界面必须标注项目生成图卡",
            "不能把 fallback 当作 image_gen PNG 完成状态",
            "听赏活动必须保留先听后选的流程",
        ],
    },
    "body_action_card_pack": {
        "classroom_role": "替代实体身体动作卡，用于稳定拍、强弱拍和身体打击编创。",
        "authenticity_policy": "动作卡是课堂符号组件，不需要真实照片；动作含义必须清楚且适合小学课堂安全执行。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "project_generated_svg",
            "save_policy": "项目内 SVG 已就绪；新增动作必须绑定节拍、节奏、强弱或休止等音乐要素。",
        },
        "quality_gates": [
            "动作必须对应音乐要素",
            "低段动作优先拍手、拍腿、跺脚、停住",
            "不得把动作卡做成与音乐无关的奖励",
            "学生操作记录可导出",
        ],
    },
    "reward_badge_pack": {
        "classroom_role": "替代实体奖励贴纸，但只奖励可观察的音乐表现证据。",
        "authenticity_policy": "徽章是项目生成符号，不涉及真实素材；不得用速度排名替代音乐评价。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "project_generated_svg",
            "save_policy": "项目内 SVG 已就绪；新增徽章必须写明对应的音乐表现证据。",
        },
        "quality_gates": [
            "奖励必须绑定稳拍、聆听、合作、创编或修正证据",
            "不得只按抢答速度发奖励",
            "评价记录必须能回看",
            "适合投屏和打印",
        ],
    },
    "form_shape_card_pack": {
        "classroom_role": "替代实体曲式卡和段落卡，用于 ABA、回旋或段落排序。",
        "authenticity_policy": "曲式图形是结构符号，不是作品插画；必须回到音频段落复听。",
        "generation_requirement": {
            "status": "ready_from_manifest",
            "provider": "project_generated_svg",
            "save_policy": "项目内 SVG 已就绪；新增图形必须绑定重复、对比或段落功能。",
        },
        "quality_gates": [
            "曲式排序必须绑定音频段落",
            "学生必须说明重复或对比依据",
            "图形不能脱离音乐材料单独排序",
            "适合高段小学使用",
        ],
    },
    "classroom_stage_background_pack": {
        "classroom_role": "作为教案级场景生成合同，替代临时找图和实体背景板；具体活动生成时应按本课音乐材料、年级和活动目标生成专属场景。",
        "authenticity_policy": "场景是运行时生成情境图，不承担真实乐器、作品史料或音色证据功能；不能遮挡音乐操作组件，也不能冒充真实课堂照片。",
        "generation_requirement": {
            "status": "lesson_runtime_generation_required",
            "provider": "lesson_runtime_image_generation",
            "save_policy": "收到具体教案后生成 16:9 PNG，保存到本次活动产物 assets 目录，并在活动 manifest 记录 prompt、provider、scene_reason、file 和 ratio_check。",
        },
        "quality_gates": [
            "必须由教案主题、音乐材料、年级和活动任务触发生成",
            "生成场景保存到本次课例或活动产物目录",
            "背景接近 16:9 且无文字水印",
            "不遮挡节拍、乐器、选择和教师控制组件",
            "场景必须服务歌曲、欣赏、律动、合奏或创编情境",
            "不能把固定背景图声明为已适配本课",
        ],
    },
    "classroom_character_pack": {
        "classroom_role": "作为低段课堂任务引导和反馈角色，不承担音乐材料或真实乐器证据功能。",
        "authenticity_policy": "使用本地生图器 image2 模型或兼容生成管线生成角色图，但必须标注为生成角色；不能替代真实乐器照片或作品资料。",
        "generation_requirement": {
            "status": "auto_from_file_report",
            "provider": "image2",
            "save_policy": "通用角色 PNG 已保存到 manifest 指定路径；后续新增角色再用 codex2api/image2 逐张生成，缺图时必须保持 pending，不能用旧图或 SVG 冒充完成。",
        },
        "quality_gates": [
            "生成 PNG 文件验收通过",
            "角色不含文字、水印或危险动作",
            "角色只用于任务引导和反馈",
            "不能替代音乐材料本身",
        ],
    },
    "ui_token_pack": {
        "classroom_role": "作为 HUD、奖励面板和进度路径的运行时 token，帮助学生看见课堂进度。",
        "authenticity_policy": "运行时生成 UI token，不涉及真实照片或外部生图图片；不得把 token 当成音乐学习证据。",
        "generation_requirement": {
            "status": "runtime_generated_ready",
            "provider": "react_svg_runtime",
            "save_policy": "由前端运行时生成，不要求磁盘图片文件；样式需随组件库验收。",
        },
        "quality_gates": [
            "运行时可生成",
            "不遮挡音乐操作组件",
            "必须绑定形成性反馈或课堂进度",
            "适合投屏大字号",
        ],
    },
    "percussion_sample_pack": {
        "classroom_role": "作为虚拟打击乐的 WebAudio 音色来源，替代课堂即时操作音。",
        "authenticity_policy": "这是 WebAudio 合成音，不得标记为真实乐器采样；补真实采样时必须记录来源和许可。",
        "generation_requirement": {
            "status": "runtime_generated_ready",
            "provider": "webaudio_synthesis",
            "save_policy": "由 WebAudio 运行时生成，不要求磁盘采样文件；真实采样另建 open_sample 条目。",
        },
        "quality_gates": [
            "声音可播放",
            "不能标记为真实采样",
            "事件记录包含乐器和时间",
            "教师静音/独奏/重置可用",
        ],
    },
    "xylophone_sample_pack": {
        "classroom_role": "作为虚拟音条琴、五声宫格和唱名参考音的 SoundFont fallback。",
        "authenticity_policy": "这是 SoundFont fallback，不得标记为真实音条琴采样；必须限制目标音级。",
        "generation_requirement": {
            "status": "soundfont_fallback_ready",
            "provider": "FluidR3_GM_SoundFont",
            "save_policy": "本地 SoundFont 文件由 instrument audio verifier 验收；本 pack 不重复保存采样文件。",
        },
        "quality_gates": [
            "SoundFont 文件可加载",
            "不能标记为真实采样",
            "音高限制到本课材料",
            "回放可用",
        ],
    },
    "feedback_sfx_pack": {
        "classroom_role": "作为正确、再试、完成、升级等短反馈音效，辅助形成性反馈。",
        "authenticity_policy": "运行时合成反馈音效，不涉及真实采样；音效不能盖过音乐材料。",
        "generation_requirement": {
            "status": "runtime_generated_ready",
            "provider": "webaudio_synthesis",
            "save_policy": "由 WebAudio 运行时生成，不要求磁盘音频文件。",
        },
        "quality_gates": [
            "音效短且不刺耳",
            "不遮盖音乐材料",
            "反馈必须附音乐原因",
            "可静音或重置",
        ],
    },
}


def list_asset_pack_templates() -> list[dict[str, Any]]:
    return [validate_asset_pack_template(_build_template_from_manifest(pack)) for pack in list_asset_packs()]


def get_asset_pack_template(asset_pack_template_id: str) -> dict[str, Any]:
    manifest = get_asset_pack(asset_pack_template_id)
    return validate_asset_pack_template(_build_template_from_manifest(manifest))


def asset_pack_template_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    normalized = str(activity_id or "")
    return [
        template
        for template in list_asset_pack_templates()
        if normalized in template.get("applicable_activity_ids", [])
    ]


def validate_asset_pack_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("asset pack template must be a dict")
    missing = [
        field
        for field in REQUIRED_ASSET_PACK_TEMPLATE_FIELDS
        if field not in template or template.get(field) is None or template.get(field) == ""
    ]
    if missing:
        raise ValueError(f"asset pack template missing fields: {', '.join(missing)}")
    if template.get("version") != "asset_pack_template_v1":
        raise ValueError("asset pack template version must be asset_pack_template_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("asset pack template audience must be primary_school")
    for field in (
        "included_assets",
        "usage",
        "applicable_activity_ids",
        "music_elements",
        "student_music_practices",
        "quality_gates",
    ):
        if not isinstance(template.get(field), list) or not template[field]:
            raise ValueError(f"asset pack template {field} must be a non-empty list")
    if not isinstance(template.get("generation_requirement"), dict):
        raise ValueError("asset pack template generation_requirement must be a dict")
    requirement = template["generation_requirement"]
    for field in ("status", "provider", "save_policy"):
        if not str(requirement.get(field) or "").strip():
            raise ValueError(f"asset pack template generation_requirement missing {field}")
    if template.get("source_kind") == "doubao_generated":
        if requirement.get("provider") != "豆包生图":
            raise ValueError("doubao asset pack template must declare provider=豆包生图")
        if requirement.get("status") != "pending_generation_until_png_verified":
            raise ValueError("doubao asset pack template must stay pending until PNG verifier passes")
    return deepcopy(template)


def _build_template_from_manifest(pack: dict[str, Any]) -> dict[str, Any]:
    pack_id = pack["asset_pack_id"]
    alignment = pack["education_alignment"]
    override = TEMPLATE_OVERRIDES.get(pack_id, {})
    default_requirement = {
        "status": "ready_from_manifest",
        "provider": str(pack.get("provider") or pack.get("source") or "project_registry"),
        "save_policy": "按 manifest 中 preview 和 assets.file 指向的路径保存，并由文件校验器确认存在。",
    }
    generation_requirement = deepcopy(override.get("generation_requirement", default_requirement))
    if generation_requirement.get("status") == "auto_from_file_report":
        report = asset_pack_file_report(pack)
        generation_requirement["status"] = (
            "ready_from_manifest" if report.get("status") == "ready" else "pending_until_png_verified"
        )
    template = {
        "version": "asset_pack_template_v1",
        "asset_pack_template_id": pack_id,
        "linked_manifest_id": pack_id,
        "label": pack["label"],
        "audience": pack["audience"],
        "source_kind": pack["source"],
        "included_assets": [
            {
                "asset_id": asset["id"],
                "file": asset["file"],
                "usage": deepcopy(asset["usage"]),
                "music_element": asset["music_element"],
                "student_action": asset["student_action"],
                "accessibility_label": asset["accessibility_label"],
            }
            for asset in pack["assets"]
        ],
        "usage": deepcopy(pack["usage"]),
        "generation_requirement": generation_requirement,
        "authenticity_policy": override.get("authenticity_policy", "素材真实性按 manifest source 与 license 执行，不能超范围使用。"),
        "applicable_activity_ids": deepcopy(pack["allowed_activities"]),
        "supports_teaching_aids": deepcopy(pack["supports_teaching_aids"]),
        "supports_virtual_instruments": deepcopy(pack["supports_virtual_instruments"]),
        "supports_ensemble_controllers": deepcopy(pack.get("supports_ensemble_controllers", [])),
        "music_elements": deepcopy(alignment["music_elements"]),
        "student_music_practices": deepcopy(alignment["student_practices"]),
        "classroom_role": override.get("classroom_role", "作为小学音乐课堂活动的可投屏、可打印或可交互素材组件。"),
        "quality_gates": deepcopy(
            override.get(
                "quality_gates",
                [
                    "素材文件必须存在",
                    "必须绑定小学音乐活动",
                    "必须声明音乐要素和学生音乐实践",
                ],
            )
        ),
    }
    return template
