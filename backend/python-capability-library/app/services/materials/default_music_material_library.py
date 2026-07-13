# 在教师没有上传具体材料时，提供默认练习素材
from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_MATERIALS: dict[str, dict[str, Any]] = {
    "duple_meter": {
        "material_id": "duple_meter",
        "label": "二拍子强弱默认节拍",
        "meter": "2/4",
        "pattern": ["strong", "weak"],
        "music_elements": ["节拍", "强弱"],
        "student_music_behaviors": ["listen", "tap", "move"],
    },
    "triple_meter": {
        "material_id": "triple_meter",
        "label": "三拍子强弱默认节拍",
        "meter": "3/4",
        "pattern": ["strong", "weak", "weak"],
        "music_elements": ["节拍", "强弱"],
        "student_music_behaviors": ["listen", "tap", "move"],
    },
    "quarter_eighth_rhythm": {
        "material_id": "quarter_eighth_rhythm",
        "label": "四分/八分节奏型",
        "meter": "2/4",
        "pattern": ["quarter", "eighth_pair"],
        "music_elements": ["节奏", "稳定拍"],
        "student_music_behaviors": ["listen", "tap", "read"],
    },
    "quarter_eighth_patterns": {
        "material_id": "quarter_eighth_patterns",
        "label": "四分/八分节奏型",
        "meter": "2/4",
        "patterns": [["quarter", "quarter"], ["quarter", "eighth_pair"], ["eighth_pair", "quarter"]],
        "music_elements": ["节奏", "稳定拍"],
        "student_music_behaviors": ["listen", "tap", "read"],
    },
    "pentatonic_solfege": {
        "material_id": "pentatonic_solfege",
        "label": "do-re-mi-sol-la 音高组",
        "pitch_set": ["do", "re", "mi", "sol", "la"],
        "music_elements": ["音高", "唱名", "五声音阶"],
        "student_music_behaviors": ["listen", "sing", "play"],
    },
    "solfege_pentatonic": {
        "material_id": "solfege_pentatonic",
        "label": "do-re-mi-sol-la 音高组",
        "pitch_set": ["do", "re", "mi", "sol", "la"],
        "music_elements": ["音高", "唱名", "五声音阶"],
        "student_music_behaviors": ["listen", "sing", "play"],
    },
    "pentatonic_scale": {
        "material_id": "pentatonic_scale",
        "label": "五声音阶材料",
        "pitch_set": ["宫", "商", "角", "徵", "羽"],
        "music_elements": ["五声音阶", "创编"],
        "student_music_behaviors": ["listen", "play", "create"],
    },
    "classroom_percussion": {
        "material_id": "classroom_percussion",
        "label": "常见课堂打击乐音色",
        "instrument_pool": ["小鼓", "木鱼", "响板", "沙锤", "三角铁"],
        "music_elements": ["音色", "乐器"],
        "student_music_behaviors": ["listen", "match", "play"],
    },
    "aba_form": {
        "material_id": "aba_form",
        "label": "ABA 默认段落结构",
        "form": ["A", "B", "A"],
        "music_elements": ["曲式", "重复", "对比"],
        "student_music_behaviors": ["listen", "order", "explain"],
    },
    "lower_body_movement": {
        "material_id": "lower_body_movement",
        "label": "低年级身体律动动作",
        "actions": ["拍手", "拍腿", "跺脚", "摇摆"],
        "music_elements": ["律动", "稳定拍"],
        "student_music_behaviors": ["move", "tap"],
    },
}


def get_default_music_material(material_id: str) -> dict[str, Any]:
    material = DEFAULT_MATERIALS.get(str(material_id or ""))
    if not material:
        raise ValueError(f"unknown default music material: {material_id}")
    return {
        **deepcopy(material),
        "version": "default_music_material_v1",
        "source": "system_default_practice_material",
        "teacher_visible_label": f"系统默认练习材料：{material['label']}",
        "may_claim_lesson_grounding": False,
        "assumptions": ["未上传教案", "使用系统默认练习材料"],
        "forbidden_claims": ["来自教师教案", "来自具体教材真实乐句", "来自上传歌曲片段"],
    }


def choose_default_material_for_focus(music_focus: str) -> dict[str, Any]:
    text = str(music_focus or "")
    if "三拍" in text:
        return get_default_music_material("triple_meter")
    if "二拍" in text or "强弱" in text or "节拍" in text:
        return get_default_music_material("duple_meter")
    if "音高" in text or "唱名" in text or any(token in text.lower() for token in ("do", "re", "mi")):
        return get_default_music_material("solfege_pentatonic")
    if "五声" in text:
        return get_default_music_material("pentatonic_scale")
    if "音色" in text or "乐器" in text:
        return get_default_music_material("classroom_percussion")
    if "曲式" in text or "ABA" in text.upper():
        return get_default_music_material("aba_form")
    if "律动" in text or "身体" in text:
        return get_default_music_material("lower_body_movement")
    return get_default_music_material("quarter_eighth_patterns")


def choose_default_material_for_focus(music_focus: str) -> dict[str, Any]:
    focus = str(music_focus or "")
    if "三拍" in focus:
        return get_default_music_material("triple_meter")
    if any(word in focus for word in ("音高", "唱名", "五声")):
        return get_default_music_material("pentatonic_solfege")
    if "节奏" in focus and "强弱" not in focus:
        return get_default_music_material("quarter_eighth_rhythm")
    return get_default_music_material("duple_meter")
