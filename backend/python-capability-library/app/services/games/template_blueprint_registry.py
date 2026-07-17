# 定义游戏的稳定“骨架”，例如核心循环、HUD、交互方式、镜头和迁移任务
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TemplateBlueprint:
    template_id: str
    game_genre: str
    mechanic_core: str
    runtime_shell: str
    hud_model: str
    interaction_model: str
    visual_language: str
    learning_transfer: str
    quality_gate_profile: str
    camera_profile: str
    cartoon_role: str
    distinctiveness_tags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["distinctiveness_tags"] = list(self.distinctiveness_tags)
        return data


BLUEPRINT_REQUIRED_FIELDS: tuple[str, ...] = (
    "game_genre",
    "mechanic_core",
    "runtime_shell",
    "hud_model",
    "interaction_model",
    "visual_language",
    "learning_transfer",
    "quality_gate_profile",
    "camera_profile",
    "cartoon_role",
)


TEMPLATE_BLUEPRINTS: dict[str, TemplateBlueprint] = {
    "beat_guardian_core": TemplateBlueprint(
        template_id="beat_guardian_core",
        game_genre="arcade_guardian",
        mechanic_core="beat_guard",
        runtime_shell="beat_guardian_shell",
        hud_model="energy_combo_target",
        interaction_model="predict_downbeat_charge",
        visual_language="中心守卫、呼吸护盾、弱拍怪物、强拍震波",
        learning_transfer="通关后回到歌曲中听辨强弱拍，并用身体律动预判每小节第 1 拍。",
        quality_gate_profile="guardian_arcade_gate",
        camera_profile="side_guard_lane",
        cartoon_role="护盾充能员",
        distinctiveness_tags=("护盾充能", "强拍预判", "弱拍蓄势", "周期延伸"),
    ),
    "rhythm_echo_core": TemplateBlueprint(
        template_id="rhythm_echo_core",
        game_genre="memory_echo",
        mechanic_core="rhythm_echo",
        runtime_shell="rhythm_echo_shell",
        hud_model="demo_record_accuracy",
        interaction_model="listen_memorize_replay",
        visual_language="示范、回声波纹、录制轨道、回放校准",
        learning_transfer="通关后说出节奏型，并用口读、拍手或身体律动再表现一次。",
        quality_gate_profile="echo_memory_gate",
        camera_profile="echo_memory_console",
        cartoon_role="回声学员",
        distinctiveness_tags=("记忆回放", "回声波纹", "录制轨道", "准确率复盘"),
    ),
    "pitch_ladder_core": TemplateBlueprint(
        template_id="pitch_ladder_core",
        game_genre="map_climb",
        mechanic_core="pitch_direction",
        runtime_shell="pitch_ladder_map_shell",
        hud_model="route_position_direction",
        interaction_model="listen_choose_route",
        visual_language="地图节点、上行下行路线、角色攀爬、路径点亮",
        learning_transfer="通关后唱回音高路线，并说明旋律是上行、下行还是保持。",
        quality_gate_profile="pitch_map_gate",
        camera_profile="vertical_route_map",
        cartoon_role="音高探路者",
        distinctiveness_tags=("地图攀爬", "高低路线", "节点前进", "唱回确认"),
    ),
    "solfege_target_core": TemplateBlueprint(
        template_id="solfege_target_core",
        game_genre="target_range",
        mechanic_core="solfege_targeting",
        runtime_shell="solfege_target_shell",
        hud_model="reticle_hit_singback",
        interaction_model="listen_aim_hit_sing",
        visual_language="准星、弹道、唱名靶、命中光环",
        learning_transfer="命中后必须开口唱回目标唱名，把听辨转化成内听和模唱。",
        quality_gate_profile="solfege_target_gate",
        camera_profile="aiming_target_arena",
        cartoon_role="唱名小射手",
        distinctiveness_tags=("靶场射击", "准星锁定", "唱名命中", "唱回确认"),
    ),
    "timbre_detective_core": TemplateBlueprint(
        template_id="timbre_detective_core",
        game_genre="detective_mystery",
        mechanic_core="timbre_reasoning",
        runtime_shell="timbre_detective_shell",
        hud_model="clue_suspect_evidence",
        interaction_model="listen_investigate_drag_evidence_submit",
        visual_language="动态侦探桌面、程序化声纹、嫌疑对象、证据飞贴、破案印章",
        learning_transfer="破案后用音色词描述证据，并迁移到真实乐器或作品片段。",
        quality_gate_profile="timbre_detective_gate",
        camera_profile="detective_desk_closeup",
        cartoon_role="声音小侦探",
        distinctiveness_tags=("侦探解谜", "声音证物", "嫌疑对象", "证据推理"),
    ),
    "form_treasure_core": TemplateBlueprint(
        template_id="form_treasure_core",
        game_genre="form_treasure_map",
        mechanic_core="musical_form_mapping",
        runtime_shell="form_treasure_shell",
        hud_model="timeline_card_progress",
        interaction_model="listen_place_card_use_tool_verify",
        visual_language="动态藏宝地图、可点段落岛、桥梁点亮、工具提示、宝箱解锁",
        learning_transfer="通关后回到作品中说出 ABA、回旋或重复对比的听辨依据。",
        quality_gate_profile="form_treasure_gate",
        camera_profile="timeline_treasure_map",
        cartoon_role="曲式寻宝队",
        distinctiveness_tags=("曲式寻宝", "段落时间轴", "结构卡排列", "宝藏奖励"),
    ),
    "composition_puzzle_core": TemplateBlueprint(
        template_id="composition_puzzle_core",
        game_genre="constrained_composition_puzzle",
        mechanic_core="music_tile_composition",
        runtime_shell="composition_puzzle_shell",
        hud_model="constraint_checklist_progress",
        interaction_model="drag_arrange_audition_submit",
        visual_language="素材卡架、创编轨道、试听波纹、约束清单、通关徽章",
        learning_transfer="通关后学生演唱、拍读或说明自己的创编短句如何满足节奏和旋律约束。",
        quality_gate_profile="composition_puzzle_gate",
        camera_profile="studio_tile_table",
        cartoon_role="音乐创编师",
        distinctiveness_tags=("约束创作", "拖拽拼图", "试听验证", "教师确认"),
    ),
}


def list_template_blueprints() -> list[dict[str, Any]]:
    return [blueprint.to_dict() for blueprint in TEMPLATE_BLUEPRINTS.values()]


def get_template_blueprint(template_id: str) -> dict[str, Any] | None:
    blueprint = TEMPLATE_BLUEPRINTS.get(str(template_id or ""))
    return blueprint.to_dict() if blueprint else None


def apply_template_blueprint_contract(config: dict[str, Any], template_id: str) -> None:
    blueprint = get_template_blueprint(template_id)
    if not blueprint:
        return
    config["template_blueprint"] = deepcopy(blueprint)
    for field in BLUEPRINT_REQUIRED_FIELDS:
        config[field] = deepcopy(blueprint[field])
    config["distinctiveness_tags"] = deepcopy(blueprint["distinctiveness_tags"])


def build_blueprint_quality_gates(template_id: str, config: dict[str, Any]) -> list[dict[str, str]]:
    blueprint = get_template_blueprint(template_id)
    if not blueprint:
        return [
            {
                "id": "template_blueprint_registered",
                "label": "模板蓝图注册",
                "status": "fail",
                "detail": "当前模板还没有进入模板工厂蓝图注册表。",
            }
        ]

    required_ready = all(config.get(field) == blueprint[field] for field in BLUEPRINT_REQUIRED_FIELDS)
    tags_ready = isinstance(config.get("distinctiveness_tags"), list) and len(config.get("distinctiveness_tags", [])) >= 3
    embedded_blueprint = config.get("template_blueprint", {}) if isinstance(config.get("template_blueprint"), dict) else {}
    return [
        {
            "id": "template_blueprint_registered",
            "label": "模板蓝图注册",
            "status": "pass",
            "detail": f"{blueprint['game_genre']} / {blueprint['mechanic_core']} 已由工厂蓝图管理。",
        },
        {
            "id": "template_blueprint_contract",
            "label": "模板工厂契约",
            "status": "pass" if required_ready and tags_ready and embedded_blueprint else "fail",
            "detail": f"{config.get('runtime_shell') or '缺少外壳'} / {config.get('hud_model') or '缺少HUD'} / {config.get('quality_gate_profile') or '缺少门禁画像'}。",
        },
        {
            "id": "template_distinctiveness_contract",
            "label": "模板反同质化契约",
            "status": "pass" if required_ready and tags_ready else "fail",
            "detail": f"{config.get('game_genre') or '缺少品类'} / {config.get('runtime_shell') or '缺少外壳'}。",
        },
        {
            "id": "quality_gate_profile_ready",
            "label": "品类门禁画像",
            "status": "pass" if config.get("quality_gate_profile") == blueprint["quality_gate_profile"] else "fail",
            "detail": f"使用 {blueprint['quality_gate_profile']} 自动继承品类门禁。",
        },
    ]


def scaffold_template_blueprint(
    *,
    template_id: str,
    game_genre: str,
    mechanic_core: str,
    runtime_shell: str,
    hud_model: str,
    interaction_model: str,
) -> dict[str, Any]:
    """Return a ready-to-fill blueprint skeleton for a new template prototype."""
    return TemplateBlueprint(
        template_id=template_id,
        game_genre=game_genre,
        mechanic_core=mechanic_core,
        runtime_shell=runtime_shell,
        hud_model=hud_model,
        interaction_model=interaction_model,
        visual_language="待填写：这个游戏品类的运动、镜头、角色和反馈语言。",
        learning_transfer="待填写：游戏结束后学生如何回到听、唱、奏、说或创编。",
        quality_gate_profile=f"{game_genre}_gate",
        camera_profile=f"{game_genre}_camera",
        cartoon_role="待填写角色",
        distinctiveness_tags=("待填写差异点1", "待填写差异点2", "待填写差异点3"),
    ).to_dict()
