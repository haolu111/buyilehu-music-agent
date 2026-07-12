from __future__ import annotations

from copy import deepcopy
from typing import Any


IMAGE2_URL = "https://gpt-image-playground.cooksleep.dev"
DOUBAO_PROVIDER_LABEL = "豆包生图"
IMAGE_GEN_PROVIDER_LABEL = "image_gen"
IMAGE2_PROVIDER_LABEL = "image2"
LESSON_RUNTIME_SCENE_PROVIDER_LABEL = "lesson_runtime_image_generation"
GENERATED_INSTRUMENT_ILLUSTRATION_SOURCES = {"image_gen", "doubao", "image2"}

REQUIRED_ASSET_PACK_FIELDS = (
    "version",
    "asset_pack_id",
    "label",
    "audience",
    "asset_type",
    "source",
    "license",
    "usage",
    "allowed_templates",
    "allowed_activities",
    "supports_teaching_aids",
    "supports_virtual_instruments",
    "education_alignment",
    "preview",
    "assets",
)

REQUIRED_ASSET_FIELDS = ("id", "file", "usage", "accessibility_label", "music_element", "student_action")


def _asset(
    asset_id: str,
    accessibility_label: str,
    usage: list[str],
    *,
    music_element: str,
    student_action: str,
    file_ext: str = "png",
) -> dict[str, Any]:
    return {
        "id": asset_id,
        "file": f"images/{asset_id}.{file_ext}",
        "usage": usage,
        "accessibility_label": accessibility_label,
        "music_element": music_element,
        "student_action": student_action,
    }


def _real_instrument_photo(
    asset_id: str,
    accessibility_label: str,
    *,
    music_element: str,
    student_action: str,
    source_url: str,
    license_name: str,
    attribution: str,
    usage: list[str] | None = None,
) -> dict[str, Any]:
    asset = _asset(
        asset_id,
        accessibility_label,
        usage or ["instrument_card", "timbre_choice", "instrument_family_sorting"],
        music_element=music_element,
        student_action=student_action,
        file_ext="jpg",
    )
    asset.update(
        {
            "visual_authenticity": "real_photo",
            "source_url": source_url,
            "source_name": "Wikimedia Commons",
            "license": license_name,
            "attribution": attribution,
        }
    )
    return asset


def _generated_playable_instrument_asset(
    asset_id: str,
    accessibility_label: str,
    prompt: str,
    *,
    music_element: str = "音色",
    student_action: str = "play",
) -> dict[str, Any]:
    asset = _asset(
        asset_id,
        f"{accessibility_label}生成插图",
        ["virtual_instrument_skin", "playable_instrument_card"],
        music_element=music_element,
        student_action=student_action,
    )
    asset.update(
        {
            "visual_authenticity": "generated_illustration",
            "source": "image2",
            "image2_url": IMAGE2_URL,
            "image2_prompt": _image2_prompt(prompt),
        }
    )
    return asset


def _image2_prompt(primary_request: str) -> str:
    return (
        "Use case: stylized-concept\n"
        "Asset type: classroom music game asset\n"
        f"Primary request: {primary_request}\n"
        "Style: 明亮、干净、儿童友好、适合投屏，边缘清晰\n"
        "Constraints: 无文字、无 logo、无水印、无危险动作、不要复杂背景\n"
        "Composition: 主体居中，四周留白，便于裁切成游戏素材\n"
        "Output: raster image for H5 classroom activity"
    )


def _doubao_pack_prompt(primary_request: str) -> str:
    return (
        f"{primary_request}"
        "风格：儿童友好、明亮干净、主体明确、适合小学音乐课堂投屏。"
        "要求：不要文字、不要 logo、不要水印；如果不是可追溯真实照片，不能冒充真实乐器。"
        "生成后必须下载为 PNG 并保存到 manifest 指定路径。"
    )


def _alignment(
    primary_competency: str,
    music_elements: list[str],
    student_practices: list[str],
    grade_bands: list[str],
    pedagogy_notes: list[str],
) -> dict[str, Any]:
    return {
        "primary_competency": primary_competency,
        "music_elements": music_elements,
        "student_practices": student_practices,
        "grade_bands": grade_bands,
        "pedagogy_notes": pedagogy_notes,
    }


ASSET_PACK_REGISTRY: dict[str, dict[str, Any]] = {
    "primary_instrument_card_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "primary_instrument_card_pack",
        "label": "小学乐器卡包",
        "audience": "primary_school",
        "asset_type": "image_pack",
        "source": "open_license_real_photos",
        "license": "mixed_open_license_real_photos",
        "usage": ["instrument_card", "timbre_choice", "orff_ensemble", "virtual_instrument_icon"],
        "allowed_templates": ["timbre_detective_core", "composition_puzzle_core", "instrument_family_sort_core"],
        "allowed_activities": ["instrument_timbre_match", "instrument_family_sorting", "orff_percussion_ensemble", "classroom_band_roles", "xylophone_creation"],
        "supports_teaching_aids": ["instrument_evidence_cards", "group_mission_cards"],
        "supports_virtual_instruments": ["virtual_hand_drum", "woodblock_claves", "shaker", "triangle_bell", "virtual_xylophone"],
        "supports_ensemble_controllers": ["classroom_percussion_kit"],
        "education_alignment": _alignment(
            "艺术表现",
            ["音色", "节奏", "乐器"],
            ["listen", "play", "match", "perform"],
            ["middle_primary", "upper_primary"],
            ["乐器图卡必须和真实音色或虚拟乐器声音绑定，避免只看图猜名称。", "打击乐图卡用于声部进入、合奏倾听和音色证据表达。"],
        ),
        "preview": "/static/assets/primary-asset-packs/primary_instrument_card_pack/preview.png",
        "assets": [
            _real_instrument_photo(
                "dizi",
                "笛子真实照片",
                music_element="音色",
                student_action="listen",
                source_url="https://commons.wikimedia.org/wiki/File:Dizi_MET_MIDP89.4.62.jpg",
                license_name="CC0",
                attribution="The Metropolitan Museum of Art",
            ),
            _real_instrument_photo(
                "erhu",
                "二胡真实照片",
                music_element="音色",
                student_action="listen",
                source_url="https://commons.wikimedia.org/wiki/File:Erh-hu,_China,_unknown_maker,_c._1900,_wood,_snake_skin,_animal_gut_-_Museum_of_New_Zealand_Te_Papa_Tongarewa_-_Wellington,_NZ_-_DSC09723.jpg",
                license_name="Public domain",
                attribution="Museum of New Zealand Te Papa Tongarewa",
            ),
            _real_instrument_photo(
                "pipa",
                "琵琶真实照片",
                music_element="音色",
                student_action="listen",
                source_url="https://commons.wikimedia.org/wiki/File:Pipa_MET_DP216711.jpg",
                license_name="CC0",
                attribution="The Metropolitan Museum of Art",
            ),
            _real_instrument_photo(
                "hand_drum",
                "小鼓真实照片",
                music_element="节奏",
                student_action="play",
                source_url="https://commons.wikimedia.org/wiki/File:Armistice_Day_hand_drum,_United_States,_c._1918,_rawhide,_steel,_copper,_cotton,_paint_-_Spurlock_Museum,_UIUC_-_DSC05921.jpg",
                license_name="CC0",
                attribution="Spurlock Museum, UIUC",
                usage=["instrument_card", "orff_ensemble", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "woodblock",
                "木鱼真实照片",
                music_element="音色",
                student_action="match",
                source_url="https://commons.wikimedia.org/wiki/File:Caixa_xinesa.jpg",
                license_name="CC BY-SA 4.0",
                attribution="Museu de la Música de Barcelona",
                usage=["instrument_card", "timbre_choice", "orff_ensemble", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "shaker",
                "沙锤真实照片",
                music_element="节奏",
                student_action="play",
                source_url="https://commons.wikimedia.org/wiki/File:Mar-3-flaschenk%C3%BCrbis-gourd-maraca-shaker-rassel-rattle-natural-percussion_-_Maultrommel,_Jew%27s_Harp.jpg",
                license_name="CC BY-SA 2.0",
                attribution="Maultrommel, Jew's Harp",
                usage=["instrument_card", "orff_ensemble", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "triangle",
                "三角铁真实照片",
                music_element="音色",
                student_action="listen",
                source_url="https://commons.wikimedia.org/wiki/File:F5_Triangel.jpg",
                license_name="CC0",
                attribution="Sofi Sykfont",
                usage=["instrument_card", "timbre_choice", "orff_ensemble", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "tambourine",
                "铃鼓真实照片",
                music_element="节奏",
                student_action="perform",
                source_url="https://commons.wikimedia.org/wiki/File:F44_Tamburin.tif",
                license_name="CC0",
                attribution="Unknown photographer",
                usage=["instrument_card", "orff_ensemble", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "xylophone",
                "音条琴真实照片",
                music_element="音高",
                student_action="play",
                source_url="https://commons.wikimedia.org/wiki/File:African_Xylophone_musical_instrument.jpg",
                license_name="CC0",
                attribution="Dalvin23",
                usage=["instrument_card", "virtual_instrument_icon", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "recorder",
                "竖笛真实照片",
                music_element="旋律",
                student_action="listen",
                source_url="https://commons.wikimedia.org/wiki/File:Recorders_made_by_Jack_Darach.jpg",
                license_name="CC0",
                attribution="Onthewings",
                usage=["instrument_card", "upper_primary_instrument", "instrument_family_sorting"],
            ),
            _real_instrument_photo(
                "melodica",
                "口风琴真实照片",
                music_element="旋律",
                student_action="play",
                source_url="https://commons.wikimedia.org/wiki/File:Hohner_Melodica_Soprano_and_Yamaha_Pianica.JPG",
                license_name="Public domain",
                attribution="Wikimedia Commons contributor",
                usage=["instrument_card", "upper_primary_instrument", "instrument_family_sorting"],
            ),
        ],
    },
    "generated_playable_instrument_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "generated_playable_instrument_pack",
        "label": "生成式可演奏乐器皮肤包",
        "audience": "primary_school",
        "asset_type": "image_pack",
        "source": "image2",
        "provider": IMAGE2_PROVIDER_LABEL,
        "image2_url": IMAGE2_URL,
        "image2_prompt": _image2_prompt("生成一套适合小学音乐课堂库乐队式演奏界面的写实单件乐器皮肤：节奏垫、小鼓、木鱼响板、沙锤、三角铁、铃鼓、音条琴、键盘、五声宫格、竖笛指法板、口风琴键盘板、笛子演奏板、长笛演奏板。每张图只能对应一个可点击乐器或一个明确的单件演奏面板，不能用套装图冒充可演奏乐器；笛子、长笛、竖笛必须分别生成，不能互相复用。"),
        "license": "project_generated",
        "usage": ["virtual_instrument_skin", "playable_instrument_card", "garageband_style_classroom_ui"],
        "allowed_templates": ["rhythm_echo_core", "composition_puzzle_core", "instrument_family_sort_core"],
        "allowed_activities": [
            "instrument_timbre_match",
            "instrument_family_sorting",
            "rhythm_warmup",
            "meter_body_movement",
            "steady_beat_walk",
            "strong_weak_beat_circle",
            "rhythm_question_answer",
            "xylophone_creation",
            "solfege_echo_singing",
            "orff_percussion_ensemble",
            "classroom_band_roles",
        ],
        "supports_teaching_aids": ["instrument_evidence_cards", "group_mission_cards"],
        "supports_virtual_instruments": [
            "rhythm_pad",
            "virtual_hand_drum",
            "woodblock_claves",
            "shaker",
            "triangle_bell",
            "tambourine",
            "virtual_xylophone",
            "simple_keyboard",
            "pentatonic_grid",
            "recorder_fingering_board",
            "melodica_keyboard_board",
            "dizi_playable_board",
            "flute_playable_board",
        ],
        "supports_ensemble_controllers": ["classroom_percussion_kit"],
        "education_alignment": _alignment(
            "艺术表现",
            ["音色", "节奏", "音高", "演奏姿态"],
            ["listen", "play", "create", "perform"],
            ["lower_primary", "middle_primary", "upper_primary"],
            [
                "生成图只作为库乐队式演奏界面皮肤，不声明为真实照片。",
                "可演奏皮肤必须一件乐器一张图；奥尔夫套装只能作为合奏控制器或教师总览，不进入单件可演奏皮肤。",
                "乐器皮肤必须绑定真实采样播放，不能只做静态图片。",
                "学生使用乐器皮肤时必须听见对应音色、记录演奏事件并能回放。",
            ],
        ),
        "preview": "/static/assets/primary-asset-packs/generated_playable_instrument_pack/preview.png",
        "assets": [
            _generated_playable_instrument_asset("rhythm_pad", "节奏垫", "小学音乐课堂库乐队式节奏垫，写实但儿童友好，方形演奏 pad，清晰可点击，不含文字、logo、水印。", music_element="节拍"),
            _generated_playable_instrument_asset("virtual_hand_drum", "虚拟小鼓", "小学音乐课堂可点击小鼓，真实鼓面材质，正面视角，适合 H5 演奏按钮，不含文字、logo、水印。", music_element="节奏"),
            _generated_playable_instrument_asset("woodblock_claves", "木鱼响板", "小学音乐课堂木鱼和响板组合，真实木质纹理，主体居中，适合演奏卡片，不含文字、logo、水印。", music_element="音色"),
            _generated_playable_instrument_asset("shaker", "虚拟沙锤", "小学音乐课堂一对沙锤，真实葫芦或木质质感，主体居中，适合触摸演奏，不含文字、logo、水印。", music_element="节奏"),
            _generated_playable_instrument_asset("triangle_bell", "三角铁碰铃", "小学音乐课堂三角铁和碰铃组合，金属质感清晰，带小槌但无文字，适合演奏界面。", music_element="音色"),
            _generated_playable_instrument_asset("tambourine", "虚拟铃鼓", "小学音乐课堂铃鼓，真实鼓皮和金属铃片质感，正面可点击，不含文字、logo、水印。", music_element="节奏"),
            _generated_playable_instrument_asset("virtual_xylophone", "虚拟音条琴", "小学音乐课堂音条琴，彩色音条或木质音条，带两支小槌，适合库乐队式演奏界面。", music_element="音高"),
            _generated_playable_instrument_asset("simple_keyboard", "简版键盘", "小学音乐课堂简版键盘，少量白键黑键，俯视角，适合触摸演奏，不含文字、logo、水印。", music_element="音高"),
            _generated_playable_instrument_asset("pentatonic_grid", "五声宫格乐器", "小学音乐课堂五声音阶宫格乐器，五个大音块，儿童友好，适合 do re mi sol la 创编，不含文字。", music_element="五声音阶"),
            _generated_playable_instrument_asset("recorder_fingering_board", "竖笛指法板", "小学音乐课堂竖笛指法板，竖笛和简洁孔位提示板，写实器物质感，不含文字、logo、水印。", music_element="音高"),
            _generated_playable_instrument_asset("melodica_keyboard_board", "口风琴键盘板", "小学音乐课堂口风琴键盘板，真实口风琴外观和吹嘴，俯视角，适合触摸演奏，不含文字、logo、水印。", music_element="旋律"),
            _generated_playable_instrument_asset("dizi_playable_board", "笛子", "小学音乐课堂笛子可演奏皮肤，横吹竹笛独立演奏板，清晰孔位和竹质纹理，适合触摸试听，不含文字、logo、水印；不能复用竖笛或长笛图片。", music_element="音色"),
            _generated_playable_instrument_asset("flute_playable_board", "长笛", "小学音乐课堂长笛可演奏皮肤，西洋长笛独立演奏板，银色金属质感和按键清晰，适合触摸试听，不含文字、logo、水印；不能复用竖笛或笛子图片。", music_element="音色"),
        ],
    },
    "music_mood_picture_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "music_mood_picture_pack",
        "label": "音乐情绪图卡包",
        "audience": "primary_school",
        "asset_type": "image_pack",
        "source": "image_gen_generated",
        "provider": IMAGE_GEN_PROVIDER_LABEL,
        "image_gen_prompt": _doubao_pack_prompt("生成一套适合小学低段听赏导入的音乐情绪图卡：欢快、优美、活泼、安静、庄严、神秘。"),
        "license": "project_generated",
        "usage": ["mood_card", "listening_intro", "expression_choice"],
        "allowed_templates": ["timbre_detective_core", "form_treasure_core"],
        "allowed_activities": ["picture_listening_intro", "listen_choose_explain", "exit_ticket_review"],
        "supports_teaching_aids": ["mood_picture_cards"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "审美感知",
            ["情绪", "速度", "力度"],
            ["listen", "choose", "explain"],
            ["lower_primary", "middle_primary"],
            ["情绪图卡用于初听后的表达，不替代聆听本身。", "学生选择图片后要说出速度、力度或音色等听觉依据。"],
        ),
        "preview": "/static/assets/primary-asset-packs/music_mood_picture_pack/preview.png",
        "assets": [
            _asset("cheerful", "欢快情绪图卡", ["mood_card"], music_element="情绪", student_action="choose"),
            _asset("beautiful", "优美情绪图卡", ["mood_card"], music_element="情绪", student_action="explain"),
            _asset("lively", "活泼情绪图卡", ["mood_card"], music_element="速度", student_action="choose"),
            _asset("quiet", "安静情绪图卡", ["mood_card"], music_element="力度", student_action="listen"),
            _asset("solemn", "庄严情绪图卡", ["mood_card"], music_element="力度", student_action="explain"),
            _asset("mysterious", "神秘情绪图卡", ["mood_card"], music_element="音色", student_action="explain"),
        ],
    },
    "mood_symbol_card_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "mood_symbol_card_pack",
        "label": "音乐情绪符号图卡 fallback",
        "audience": "primary_school",
        "asset_type": "svg_pack",
        "source": "project_generated",
        "license": "project_generated",
        "usage": ["mood_card", "listening_intro", "expression_choice"],
        "allowed_templates": ["timbre_detective_core", "form_treasure_core"],
        "allowed_activities": ["picture_listening_intro", "listen_choose_explain", "exit_ticket_review"],
        "supports_teaching_aids": ["mood_picture_cards"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "审美感知",
            ["情绪", "速度", "力度"],
            ["listen", "choose", "explain"],
            ["lower_primary", "middle_primary"],
            [
                "这是 image_gen PNG 不可用时的项目生成 SVG fallback，用于保证欣赏导入可直接上课。",
                "图卡只能辅助初听后的表达，学生仍必须先听音乐并说出速度、力度或旋律依据。",
            ],
        ),
        "preview": "/static/assets/primary-asset-packs/mood_symbol_card_pack/preview.svg",
        "assets": [
            _asset("cheerful", "欢快情绪符号图卡", ["mood_card"], music_element="情绪", student_action="choose", file_ext="svg"),
            _asset("beautiful", "优美情绪符号图卡", ["mood_card"], music_element="情绪", student_action="explain", file_ext="svg"),
            _asset("lively", "活泼情绪符号图卡", ["mood_card"], music_element="速度", student_action="choose", file_ext="svg"),
            _asset("quiet", "安静情绪符号图卡", ["mood_card"], music_element="力度", student_action="listen", file_ext="svg"),
            _asset("solemn", "庄严情绪符号图卡", ["mood_card"], music_element="力度", student_action="explain", file_ext="svg"),
            _asset("mysterious", "神秘情绪符号图卡", ["mood_card"], music_element="音色", student_action="explain", file_ext="svg"),
        ],
    },
    "body_action_card_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "body_action_card_pack",
        "label": "身体动作卡包",
        "audience": "primary_school",
        "asset_type": "css_svg_pack",
        "source": "project_generated",
        "license": "project_generated",
        "usage": ["body_action_card", "movement_prompt"],
        "allowed_templates": ["beat_guardian_core", "rhythm_echo_core"],
        "allowed_activities": ["meter_body_movement", "body_percussion_builder"],
        "supports_teaching_aids": ["body_percussion_cards"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "艺术表现",
            ["节拍", "节奏", "强弱"],
            ["listen", "move", "tap"],
            ["lower_primary", "middle_primary"],
            ["身体动作卡服务稳定拍和强弱感知，不作为纯动作奖励。", "低段优先用拍手、拍腿、跺脚建立可感知的拍点。"],
        ),
        "preview": "/static/assets/primary-asset-packs/body_action_card_pack/preview.svg",
        "assets": [
            _asset("clap", "拍手动作卡", ["body_action_card"], music_element="节拍", student_action="tap", file_ext="svg"),
            _asset("pat_legs", "拍腿动作卡", ["body_action_card"], music_element="强弱", student_action="move", file_ext="svg"),
            _asset("stamp", "跺脚动作卡", ["body_action_card"], music_element="强拍", student_action="move", file_ext="svg"),
            _asset("snap", "捻指动作卡", ["body_action_card"], music_element="弱拍", student_action="tap", file_ext="svg"),
            _asset("pat_shoulder", "拍肩动作卡", ["body_action_card"], music_element="节奏", student_action="perform", file_ext="svg"),
            _asset("freeze", "停住动作卡", ["body_action_card"], music_element="休止", student_action="move", file_ext="svg"),
        ],
    },
    "reward_badge_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "reward_badge_pack",
        "label": "课堂奖励徽章包",
        "audience": "primary_school",
        "asset_type": "css_svg_pack",
        "source": "project_generated",
        "license": "project_generated",
        "usage": ["reward_badge", "feedback"],
        "allowed_templates": ["beat_guardian_core", "rhythm_echo_core", "pitch_ladder_core", "composition_puzzle_core"],
        "allowed_activities": ["rhythm_warmup", "xylophone_creation", "group_relay_performance"],
        "supports_teaching_aids": ["performance_rubric"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "艺术表现",
            ["节奏", "音准", "合作", "创编"],
            ["perform", "assess", "revise"],
            ["lower_primary", "middle_primary", "upper_primary"],
            ["奖励徽章必须对应具体音乐表现证据，如稳拍、倾听、合作或创编修改。", "不把速度排名作为唯一评价，避免偏离音乐学习。"],
        ),
        "preview": "/static/assets/primary-asset-packs/reward_badge_pack/preview.svg",
        "assets": [
            _asset("steady_beat_star", "稳拍星徽章", ["reward_badge"], music_element="节拍", student_action="perform", file_ext="svg"),
            _asset("listening_star", "聆听星徽章", ["reward_badge"], music_element="聆听", student_action="listen", file_ext="svg"),
            _asset("cooperation_star", "合作星徽章", ["reward_badge"], music_element="合作", student_action="assess", file_ext="svg"),
            _asset("creation_star", "创编星徽章", ["reward_badge"], music_element="创编", student_action="revise", file_ext="svg"),
        ],
    },
    "form_shape_card_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "form_shape_card_pack",
        "label": "曲式图形卡包",
        "audience": "primary_school",
        "asset_type": "css_svg_pack",
        "source": "project_generated",
        "license": "project_generated",
        "usage": ["form_card", "timeline_symbol"],
        "allowed_templates": ["form_treasure_core"],
        "allowed_activities": ["form_ordering"],
        "supports_teaching_aids": ["form_cards"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "审美感知",
            ["曲式", "重复", "对比"],
            ["listen", "order", "explain"],
            ["upper_primary"],
            ["曲式卡必须绑定音频段落复听，不能脱离音乐材料排序。", "图形只帮助学生看见结构，最终要回到重复和对比的听觉依据。"],
        ),
        "preview": "/static/assets/primary-asset-packs/form_shape_card_pack/preview.svg",
        "assets": [
            _asset("section_a", "A 段图形卡", ["form_card"], music_element="曲式", student_action="order", file_ext="svg"),
            _asset("section_b", "B 段图形卡", ["form_card"], music_element="曲式", student_action="order", file_ext="svg"),
            _asset("section_c", "C 段图形卡", ["form_card"], music_element="曲式", student_action="order", file_ext="svg"),
            _asset("repeat", "重复图形卡", ["form_card"], music_element="重复", student_action="explain", file_ext="svg"),
            _asset("contrast", "对比图形卡", ["form_card"], music_element="对比", student_action="explain", file_ext="svg"),
        ],
    },
    "classroom_stage_background_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "classroom_stage_background_pack",
        "label": "教案级课堂场景生成合同",
        "audience": "primary_school",
        "asset_type": "runtime_scene_generation_pack",
        "source": "lesson_runtime_generated",
        "provider": LESSON_RUNTIME_SCENE_PROVIDER_LABEL,
        "generation_prompt_policy": (
            "场景图必须由智能体在收到具体教案、歌曲/欣赏材料、年级、活动类型和课堂主题后临时生成。"
            "生成结果保存到本次课例或活动产物 assets 目录，不能作为全局固定背景冒充已入库素材。"
        ),
        "license": "project_generated_runtime",
        "usage": ["activity_background", "game_scene_background"],
        "allowed_templates": ["beat_guardian_core", "pitch_ladder_core", "timbre_detective_core", "form_treasure_core", "composition_puzzle_core"],
        "allowed_activities": ["rhythm_warmup", "picture_listening_intro", "listen_choose_explain", "orff_percussion_ensemble", "xylophone_creation"],
        "supports_teaching_aids": [],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "审美感知",
            ["情境", "情绪", "音乐形象"],
            ["listen", "move", "perform"],
            ["lower_primary", "middle_primary", "upper_primary"],
            [
                "背景只承担课堂情境和空间提示，不能遮挡音乐操作组件。",
                "场景必须从本课音乐材料、活动任务和年级特征生成，避免把固定风景套到所有作品上。",
                "生成后要保存到本次课例产物目录，并记录 prompt、provider、比例和使用活动。",
            ],
        ),
        "preview": "/static/assets/primary-asset-packs/classroom_stage_background_pack/runtime-scene-contract.json",
        "assets": [
            _asset("lesson_story_scene", "按教案主题生成的课堂故事场景", ["activity_background"], music_element="情境", student_action="listen", file_ext="json"),
            _asset("movement_path_scene", "按节拍或律动任务生成的运动路径场景", ["game_scene_background"], music_element="节拍", student_action="move", file_ext="json"),
            _asset("listening_imagery_scene", "按欣赏音乐形象生成的听赏想象场景", ["activity_background"], music_element="音乐形象", student_action="explain", file_ext="json"),
            _asset("performance_stage_scene", "按展示或合奏任务生成的表演舞台场景", ["activity_background"], music_element="展示", student_action="perform", file_ext="json"),
            _asset("form_route_scene", "按曲式段落生成的音乐路线场景", ["game_scene_background"], music_element="结构", student_action="order", file_ext="json"),
        ],
    },
    "classroom_character_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "classroom_character_pack",
        "label": "课堂音乐角色包",
        "audience": "primary_school",
        "asset_type": "image_pack",
        "source": "image2",
        "provider": IMAGE2_PROVIDER_LABEL,
        "image2_url": IMAGE2_URL,
        "image2_prompt": _image2_prompt("生成适合小学音乐课堂互动游戏的通用角色包：音乐小助手、节奏队长、音色侦探。每张图必须是单独角色，不要合集，不要文字、logo、水印。角色只用于任务引导和反馈，不能替代音乐材料或真实乐器照片。"),
        "license": "project_generated",
        "usage": ["classroom_character", "game_feedback_character", "mission_guide"],
        "allowed_templates": ["rhythm_echo_core", "timbre_detective_core", "composition_puzzle_core"],
        "allowed_activities": ["rhythm_warmup", "instrument_timbre_match", "xylophone_creation", "lesson_opening_hook"],
        "supports_teaching_aids": [],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "审美感知",
            ["课堂情境", "音乐形象", "反馈"],
            ["listen", "perform", "revise"],
            ["lower_primary", "middle_primary"],
            ["角色只承担任务引导和反馈陪伴，不能替代音乐材料本身。", "角色形象必须儿童友好、无文字水印，并且不冒充真实乐器照片。"],
        ),
        "preview": "/static/assets/primary-asset-packs/classroom_character_pack/preview.png",
        "assets": [
            _asset("music_helper", "音乐小助手角色", ["classroom_character"], music_element="课堂情境", student_action="listen"),
            _asset("rhythm_captain", "节奏队长角色", ["classroom_character"], music_element="节奏", student_action="tap"),
            _asset("timbre_detective", "音色侦探角色", ["classroom_character"], music_element="音色", student_action="explain"),
        ],
    },
    "ui_token_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "ui_token_pack",
        "label": "课堂游戏 UI token 包",
        "audience": "primary_school",
        "asset_type": "runtime_svg_pack",
        "source": "runtime_generated",
        "license": "project_generated_runtime",
        "usage": ["game_hud", "progress_path", "reward_panel"],
        "allowed_templates": ["beat_guardian_core", "rhythm_echo_core", "form_treasure_core", "composition_puzzle_core"],
        "allowed_activities": ["rhythm_warmup", "form_ordering", "xylophone_creation", "group_relay_performance"],
        "supports_teaching_aids": ["performance_rubric"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "艺术表现",
            ["反馈", "课堂进度", "音乐任务"],
            ["perform", "revise", "assess"],
            ["lower_primary", "middle_primary", "upper_primary"],
            ["UI token 服务课堂状态和形成性反馈，不替代音乐依据。", "星星、能量、路线点必须绑定音乐表现证据。"],
        ),
        "preview": "/static/assets/primary-asset-packs/ui_token_pack/runtime-preview.svg",
        "assets": [
            _asset("star", "星星 token", ["game_hud", "reward_panel"], music_element="反馈", student_action="revise", file_ext="svg"),
            _asset("energy", "能量 token", ["game_hud"], music_element="课堂进度", student_action="perform", file_ext="svg"),
            _asset("key", "钥匙 token", ["progress_path"], music_element="任务推进", student_action="perform", file_ext="svg"),
            _asset("treasure", "宝箱 token", ["reward_panel"], music_element="完成反馈", student_action="assess", file_ext="svg"),
            _asset("route_dot", "路线点 token", ["progress_path"], music_element="学习路径", student_action="revise", file_ext="svg"),
        ],
    },
    "percussion_sample_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "percussion_sample_pack",
        "label": "课堂打击乐 WebAudio 音色包",
        "audience": "primary_school",
        "asset_type": "runtime_audio_pack",
        "source": "webaudio_synthesis",
        "license": "project_generated_synthesis",
        "usage": ["virtual_instrument_sound", "orff_ensemble", "rhythm_feedback"],
        "allowed_templates": ["rhythm_echo_core", "body_percussion_core", "orff_ensemble_core"],
        "allowed_activities": ["rhythm_warmup", "meter_body_movement", "orff_percussion_ensemble", "classroom_band_roles"],
        "supports_teaching_aids": ["rhythm_cards", "body_percussion_cards", "group_mission_cards"],
        "supports_virtual_instruments": ["virtual_hand_drum", "woodblock_claves", "shaker", "triangle_bell", "tambourine"],
        "supports_ensemble_controllers": ["classroom_percussion_kit"],
        "education_alignment": _alignment(
            "艺术表现",
            ["节奏", "音色", "合奏"],
            ["tap", "play", "perform"],
            ["lower_primary", "middle_primary", "upper_primary"],
            ["WebAudio 打击音可替代课堂即时操作音，但不能标记为真实采样。", "合奏音色必须服务声部进入、强弱和稳定拍。"],
        ),
        "preview": "/static/assets/primary-asset-packs/percussion_sample_pack/runtime-audio-preview.json",
        "assets": [
            _asset("hand_drum_synth", "小鼓 WebAudio 合成音", ["virtual_instrument_sound"], music_element="节奏", student_action="play", file_ext="json"),
            _asset("woodblock_synth", "木鱼 WebAudio 合成音", ["virtual_instrument_sound"], music_element="音色", student_action="tap", file_ext="json"),
            _asset("shaker_synth", "沙锤 WebAudio 合成音", ["virtual_instrument_sound"], music_element="弱拍", student_action="perform", file_ext="json"),
            _asset("triangle_synth", "三角铁 WebAudio 合成音", ["virtual_instrument_sound"], music_element="音色", student_action="listen", file_ext="json"),
            _asset("tambourine_synth", "铃鼓 WebAudio 合成音", ["virtual_instrument_sound"], music_element="节奏", student_action="perform", file_ext="json"),
        ],
    },
    "xylophone_sample_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "xylophone_sample_pack",
        "label": "音条琴 SoundFont 音色包",
        "audience": "primary_school",
        "asset_type": "runtime_audio_pack",
        "source": "soundfont_fallback",
        "license": "FluidR3 GM SoundFont",
        "usage": ["virtual_xylophone_sound", "solfege_reference", "creation_playback"],
        "allowed_templates": ["pitch_ladder_core", "composition_puzzle_core"],
        "allowed_activities": ["xylophone_creation", "solfege_sorting", "solfege_echo_singing"],
        "supports_teaching_aids": ["solfege_cards", "pitch_ladder_board"],
        "supports_virtual_instruments": ["virtual_xylophone", "pentatonic_grid", "simple_keyboard", "melodica_keyboard_board"],
        "education_alignment": _alignment(
            "艺术表现",
            ["音高", "唱名", "创编"],
            ["listen", "play", "create"],
            ["middle_primary", "upper_primary"],
            ["SoundFont 可作为课堂可听 fallback，不能标记为真实音条琴采样。", "音高活动必须限制目标音级，避免乱敲。"],
        ),
        "preview": "/static/assets/primary-asset-packs/xylophone_sample_pack/soundfont-preview.json",
        "assets": [
            _asset("xylophone_soundfont", "音条琴 SoundFont", ["virtual_xylophone_sound"], music_element="音高", student_action="play", file_ext="json"),
            _asset("pentatonic_grid_soundfont", "五声宫格 SoundFont 映射", ["creation_playback"], music_element="五声", student_action="create", file_ext="json"),
            _asset("solfege_reference_tone", "唱名参考音", ["solfege_reference"], music_element="唱名", student_action="listen", file_ext="json"),
        ],
    },
    "feedback_sfx_pack": {
        "version": "asset_pack_manifest_v1",
        "asset_pack_id": "feedback_sfx_pack",
        "label": "课堂反馈 WebAudio 音效包",
        "audience": "primary_school",
        "asset_type": "runtime_audio_pack",
        "source": "webaudio_synthesis",
        "license": "project_generated_synthesis",
        "usage": ["feedback_sfx", "reward_panel", "tap_feedback"],
        "allowed_templates": ["beat_guardian_core", "rhythm_echo_core", "timbre_detective_core", "composition_puzzle_core"],
        "allowed_activities": ["rhythm_warmup", "instrument_timbre_match", "xylophone_creation", "show_and_peer_feedback"],
        "supports_teaching_aids": ["performance_rubric"],
        "supports_virtual_instruments": [],
        "education_alignment": _alignment(
            "艺术表现",
            ["反馈", "修正", "完成"],
            ["revise", "assess", "perform"],
            ["lower_primary", "middle_primary", "upper_primary"],
            ["反馈音效必须短、不刺耳，并且服务形成性反馈。", "正确、错误、完成、升级音效不能盖过音乐材料本身。"],
        ),
        "preview": "/static/assets/primary-asset-packs/feedback_sfx_pack/runtime-sfx-preview.json",
        "assets": [
            _asset("correct_chime", "正确提示音", ["feedback_sfx"], music_element="反馈", student_action="revise", file_ext="json"),
            _asset("try_again_tone", "再试一次提示音", ["feedback_sfx"], music_element="修正", student_action="revise", file_ext="json"),
            _asset("complete_chime", "完成提示音", ["feedback_sfx"], music_element="完成", student_action="perform", file_ext="json"),
            _asset("level_up_chime", "升级提示音", ["feedback_sfx"], music_element="挑战", student_action="perform", file_ext="json"),
        ],
    },
}


def list_asset_packs() -> list[dict[str, Any]]:
    return [validate_asset_pack_manifest(pack) for pack in ASSET_PACK_REGISTRY.values()]


def get_asset_pack(asset_pack_id: str) -> dict[str, Any]:
    pack = ASSET_PACK_REGISTRY.get(str(asset_pack_id or ""))
    if not pack:
        raise ValueError(f"unknown asset pack: {asset_pack_id}")
    return validate_asset_pack_manifest(pack)


def validate_asset_pack_manifest(pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("asset pack manifest must be a dict")
    missing = [
        field
        for field in REQUIRED_ASSET_PACK_FIELDS
        if field not in pack or pack.get(field) is None or pack.get(field) == ""
    ]
    if missing:
        raise ValueError(f"asset pack manifest missing fields: {', '.join(missing)}")
    if pack.get("version") != "asset_pack_manifest_v1":
        raise ValueError("asset pack manifest version must be asset_pack_manifest_v1")
    if pack.get("audience") != "primary_school":
        raise ValueError("asset pack audience must be primary_school")
    if pack.get("source") == "image2":
        if pack.get("image2_url") != IMAGE2_URL:
            raise ValueError("image2 asset pack must use the configured image2 URL")
        if not str(pack.get("image2_prompt") or "").strip():
            raise ValueError("image2 asset pack must include image2_prompt")
        if pack.get("license") != "project_generated":
            raise ValueError("image2 asset pack license must be project_generated")
    if pack.get("source") == "doubao_generated":
        if pack.get("provider") != DOUBAO_PROVIDER_LABEL:
            raise ValueError("doubao asset pack must declare provider=豆包生图")
        if not str(pack.get("doubao_prompt") or "").strip():
            raise ValueError("doubao asset pack must include doubao_prompt")
        if pack.get("license") != "project_generated":
            raise ValueError("doubao asset pack license must be project_generated")
    if pack.get("source") == "image_gen_generated":
        if pack.get("provider") != IMAGE_GEN_PROVIDER_LABEL:
            raise ValueError("image_gen asset pack must declare provider=image_gen")
        if not str(pack.get("image_gen_prompt") or "").strip():
            raise ValueError("image_gen asset pack must include image_gen_prompt")
        if pack.get("license") != "project_generated":
            raise ValueError("image_gen asset pack license must be project_generated")
    if pack.get("source") == "lesson_runtime_generated":
        if pack.get("provider") != LESSON_RUNTIME_SCENE_PROVIDER_LABEL:
            raise ValueError("lesson runtime scene pack must declare provider=lesson_runtime_image_generation")
        if not str(pack.get("generation_prompt_policy") or "").strip():
            raise ValueError("lesson runtime scene pack must include generation_prompt_policy")
        if pack.get("license") != "project_generated_runtime":
            raise ValueError("lesson runtime scene pack license must be project_generated_runtime")
    assets = pack.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("asset pack assets must be a non-empty list")
    _validate_alignment(pack.get("education_alignment"))
    for asset in assets:
        _validate_asset_item(asset)
    return deepcopy(pack)


def _validate_asset_item(asset: dict[str, Any]) -> None:
    if not isinstance(asset, dict):
        raise ValueError("asset item must be a dict")
    missing = [field for field in REQUIRED_ASSET_FIELDS if not asset.get(field)]
    if missing:
        raise ValueError(f"asset item missing fields: {', '.join(missing)}")
    if not isinstance(asset.get("usage"), list) or not asset["usage"]:
        raise ValueError("asset item usage must be a non-empty list")
    _validate_instrument_visual_authenticity(asset)


def _validate_instrument_visual_authenticity(asset: dict[str, Any]) -> None:
    usage = set(asset.get("usage") or [])
    if not usage.intersection({"instrument_card", "timbre_choice", "instrument_family_sorting", "virtual_instrument_icon"}):
        return
    authenticity = str(asset.get("visual_authenticity") or "")
    if authenticity == "real_photo":
        missing = [field for field in ("source_url", "license", "attribution") if not asset.get(field)]
        if missing:
            raise ValueError(f"real instrument photo missing fields: {', '.join(missing)}")
        return
    if authenticity == "generated_illustration":
        label = str(asset.get("accessibility_label") or "")
        source = str(asset.get("source") or "")
        if source not in GENERATED_INSTRUMENT_ILLUSTRATION_SOURCES:
            raise ValueError("generated instrument illustration must declare source=image_gen, doubao, or image2")
        prompt = str(asset.get("image_gen_prompt") or asset.get("doubao_prompt") or asset.get("image2_prompt") or "").strip()
        if not prompt:
            raise ValueError("generated instrument illustration must include image_gen_prompt, doubao_prompt, or image2_prompt")
        if source == "image2" and asset.get("image2_url") != IMAGE2_URL:
            raise ValueError("image2 generated instrument illustration must include the configured image2_url")
        if "生成插图" not in label and "待补真实照片" not in label and "非真实" not in label:
            raise ValueError("generated instrument illustration must be labeled as generated or pending real photo")
        return
    raise ValueError("instrument visual asset must declare visual_authenticity as real_photo or generated_illustration")


def _validate_alignment(alignment: Any) -> None:
    if not isinstance(alignment, dict):
        raise ValueError("asset pack education_alignment must be a dict")
    required = ("primary_competency", "music_elements", "student_practices", "grade_bands", "pedagogy_notes")
    missing = [field for field in required if not alignment.get(field)]
    if missing:
        raise ValueError(f"asset pack education_alignment missing fields: {', '.join(missing)}")
    if alignment["primary_competency"] not in {"审美感知", "艺术表现", "创意实践", "文化理解"}:
        raise ValueError("asset pack primary_competency is not supported")
    for field in ("music_elements", "student_practices", "grade_bands", "pedagogy_notes"):
        if not isinstance(alignment.get(field), list) or not alignment[field]:
            raise ValueError(f"asset pack education_alignment.{field} must be a non-empty list")
