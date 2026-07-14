from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


MAX_LESSON_CHARS = 4200
SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}

MUSIC_ELEMENT_KEYWORDS = {
    "节奏与时值": ["节奏", "节拍", "拍子", "时值", "四分", "二分", "全音符", "附点", "切分", "稳定拍"],
    "旋律与音高": ["旋律", "音高", "模唱", "视唱", "音阶", "上行", "下行", "级进", "跳进"],
    "音色听辨": ["音色", "乐器", "管弦", "民族乐器", "打击乐", "钢琴", "小提琴", "长笛", "古筝"],
    "力度与速度": ["力度", "强弱", "速度", "渐强", "渐弱", "快", "慢", "情绪变化"],
    "调式与民族风格": ["五声", "宫调", "商调", "徵调", "羽调", "民族", "民歌", "调式"],
    "歌词与音乐形象": ["歌词", "形象", "情景", "角色", "故事", "情绪", "意境"],
    "演唱表现": ["演唱", "歌唱", "咬字", "气息", "连贯", "表现", "表演"],
    "创编实践": ["创编", "编创", "即兴", "合作", "小组", "展示", "改编"],
}

FLOW_KEYWORDS = [
    "导入",
    "聆听",
    "欣赏",
    "学唱",
    "模唱",
    "律动",
    "拍击",
    "创编",
    "合作",
    "展示",
    "评价",
]

STAGE_TASK_TYPE_MAP = {
    "导入": "motivation_entry",
    "聆听": "listen_discriminate",
    "欣赏": "listen_discriminate",
    "学唱": "sing_practice",
    "模唱": "sing_practice",
    "律动": "rhythm_perform",
    "拍击": "rhythm_perform",
    "创编": "creative_construction",
    "合作": "collaborative_task",
    "展示": "showcase_reflection",
    "评价": "showcase_reflection",
}

TASK_TYPE_GAMEABLE_POINTS = {
    "motivation_entry": "更适合作为情境引入，不宜直接做成主游戏。",
    "listen_discriminate": "适合把听辨结果转成匹配、选择、定位或排序操作。",
    "sing_practice": "适合把唱名、乐句、模唱或听唱要求转成拖拽、应答或跟唱挑战。",
    "rhythm_perform": "适合把拍点、强弱、节奏型转成拖拽排序、跟拍或动作闯关。",
    "creative_construction": "适合把创编要求拆成拼接、补全、改写或双声部任务。",
    "collaborative_task": "适合做成小组协作挑战或轮流接力任务。",
    "showcase_reflection": "更适合作为游戏后的表达、展示和评价闭环。",
}

TASK_TYPE_LABELS = {
    "motivation_entry": "情境导入",
    "listen_discriminate": "聆听辨析",
    "sing_practice": "演唱练习",
    "rhythm_perform": "节奏表现",
    "creative_construction": "创编建构",
    "collaborative_task": "合作任务",
    "showcase_reflection": "展示评价",
}

MIDDLE_LAYER_RULES = [
    "先识别整课目标，再定位最适合游戏化的教学环节。",
    "优先选择能让学生直接操作并即时反馈的核心练习环节。",
    "导入和总结一般不单独作为主游戏，除非教案明确要求。",
    "主游戏必须同时对齐具体音乐要素、环节任务和整课学习目标。",
]

MUSICAL_GAME_LOGIC_CONTRACT = {
    "version": "musical_game_logic_v1",
    "non_negotiables": [
        "游戏操作必须对应一个可听、可唱、可拍、可辨或可创编的音乐行为。",
        "正确答案不能只靠文字或图片判断，必须能回到声音、节拍、音高、力度、音色或乐句证据。",
        "播放、试听、跟拍、模唱、节奏反馈或音高反馈至少出现一种。",
        "每个反馈都要说明音乐原因，而不是只显示对错。",
        "通关后必须回到课堂表达：唱一唱、拍一拍、说一说或创编展示。",
    ],
    "loop": ["音乐输入", "学生操作", "声音或节拍反馈", "音乐理由表达", "课堂迁移"],
}

LESSON_PROMPT_CHAIN = [
    {
        "step": "lesson_understanding",
        "name": "整课理解",
        "instruction": "先提炼课题、学段、课型、整课目标和教学重难点，不要把单个知识点误当整节课。",
        "output": ["lesson_profile", "whole_class_goals"],
    },
    {
        "step": "segment_cardization",
        "name": "环节卡片化",
        "instruction": "把教案流程拆成标准化环节卡，每张卡必须包含环节任务、学生动作、音乐焦点和课堂证据。",
        "output": ["lesson_segments"],
    },
    {
        "step": "gameability_judgement",
        "name": "游戏化判定",
        "instruction": "按目标对齐、音乐要素清晰度、学生可操作性、反馈可见性和课堂位置给每张环节卡评分。",
        "output": ["goal_task_game_mapping", "selected_game_segment"],
    },
    {
        "step": "mechanic_mapping",
        "name": "机制映射",
        "instruction": "根据音乐要素选择游戏机制，机制必须让学生通过操作理解音乐，而不只是看动画。",
        "output": ["music_element_mechanic", "recommended_game"],
    },
    {
        "step": "teaching_closure",
        "name": "教学闭环",
        "instruction": "生成后必须回到课堂表达、演唱、拍击、创编或评价，证明游戏服务学习。",
        "output": ["assessment_closure", "lesson_fit_rubric"],
    },
]

STANDARD_SEGMENT_CARD_SCHEMA = {
    "version": "lesson_segment_card_v1",
    "required_fields": [
        "segment_id",
        "sequence_no",
        "stage_label",
        "task_type",
        "task_summary",
        "music_focus",
        "objective_links",
        "student_operation",
        "gameable_point",
        "music_element_mechanic",
        "score_breakdown",
        "gameability_score",
        "selection_reason",
    ],
    "score_fields": {
        "objective_alignment": "是否承接整课目标。",
        "music_focus_alignment": "是否指向明确音乐要素。",
        "student_operation": "学生是否能直接拖拽、点击、拍击、演唱或创编。",
        "feedback_visibility": "结果是否能即时听到、看到或被教师判断。",
        "classroom_position": "是否处在核心练习、聆听、表现或创编环节。",
    },
}

SEGMENT_SELECTION_WEIGHTS = {
    "objective_alignment": 24,
    "music_focus_alignment": 22,
    "student_operation": 20,
    "feedback_visibility": 18,
    "classroom_position": 16,
}

MUSIC_ELEMENT_MECHANIC_RULES = [
    {
        "rule_id": "rhythm_duration_to_race_or_grid",
        "categories": ["节奏与时值"],
        "keywords": ["节奏", "节拍", "拍子", "时值", "切分", "附点", "休止符", "强弱"],
        "mechanism_id": "rhythm_drag_playback",
        "game_type": "rhythm_race_game",
        "game_name": "节奏行动挑战",
        "operation_mode": "拖拽排序 + 播放验证 + 跟拍表现",
        "visual_metaphor": "角色赛跑、节拍格、旗帜、红绿灯或弹跳轨道",
        "feedback": "播放时按拍点依次高亮，错误位置给出重听和重排提示。",
        "student_actions": ["拖拽节奏角色", "点击播放验证", "跟随拍击", "说出节奏理由"],
    },
    {
        "rule_id": "melody_pitch_to_path",
        "categories": ["旋律与音高"],
        "keywords": ["旋律", "音高", "上行", "下行", "级进", "跳进", "乐句", "模唱"],
        "mechanism_id": "melody_path_builder",
        "game_type": "pitch_path_game",
        "game_name": "旋律路线挑战",
        "operation_mode": "连接音高点 + 播放验证 + 模唱回应",
        "visual_metaphor": "山坡路线、音高阶梯、问答卡或旋律轨迹",
        "feedback": "路线随音高起伏播放，错误处提示重新听辨高低变化。",
        "student_actions": ["听辨旋律", "连接路线", "播放验证", "模唱回应"],
    },
    {
        "rule_id": "timbre_to_detective_match",
        "categories": ["音色听辨"],
        "keywords": ["音色", "乐器", "管弦", "民族乐器", "小提琴", "长笛", "古筝", "二胡"],
        "mechanism_id": "timbre_detective_match",
        "game_type": "timbre_match_game",
        "game_name": "音色侦探",
        "operation_mode": "听音色 + 拖拽匹配 + 说明依据",
        "visual_metaphor": "侦探卡、乐器线索、角色身份牌",
        "feedback": "匹配后显示发声特点提示，答错可重新听。",
        "student_actions": ["聆听音色", "匹配乐器", "说明音色依据"],
    },
    {
        "rule_id": "dynamics_tempo_to_control_panel",
        "categories": ["力度与速度"],
        "keywords": ["力度", "强弱", "速度", "渐强", "渐弱", "快", "慢"],
        "mechanism_id": "expression_control_panel",
        "game_type": "expression_control_game",
        "game_name": "音乐表情控制台",
        "operation_mode": "调节滑杆 + 对比播放 + 情绪判断",
        "visual_metaphor": "速度仪表盘、力度调色盘、情绪能量条",
        "feedback": "画面运动和音量随选择变化，学生对比后解释判断。",
        "student_actions": ["聆听片段", "调节力度或速度", "对比反馈", "说明音乐形象"],
    },
    {
        "rule_id": "mode_style_to_puzzle",
        "categories": ["调式与民族风格"],
        "keywords": ["五声", "宫", "商", "角", "徵", "羽", "民族", "调式", "民歌"],
        "mechanism_id": "mode_phrase_puzzle",
        "game_type": "mode_puzzle_game",
        "game_name": "民族调式拼图",
        "operation_mode": "选择音级 + 拼接短句 + 播放风格",
        "visual_metaphor": "五声音级宫格、民族纹样拼图、旋律积木",
        "feedback": "只允许使用目标音级，播放后提示是否具有课例风格。",
        "student_actions": ["选择音级", "拼接短句", "播放试听", "分享风格判断"],
    },
    {
        "rule_id": "lyrics_image_to_scene_choice",
        "categories": ["歌词与音乐形象"],
        "keywords": ["歌词", "形象", "情景", "角色", "故事", "情绪", "意境"],
        "mechanism_id": "music_scene_choice",
        "game_type": "scene_expression_game",
        "game_name": "音乐形象剧场",
        "operation_mode": "选择情景角色 + 匹配音乐证据 + 表演回应",
        "visual_metaphor": "舞台角色、情景卡、表情贴纸",
        "feedback": "选择后要求指出歌词或音乐依据，避免只凭图片猜。",
        "student_actions": ["聆听或朗读歌词", "选择形象卡", "匹配音乐证据", "表演回应"],
    },
    {
        "rule_id": "singing_to_response_ladder",
        "categories": ["演唱表现"],
        "keywords": ["演唱", "歌唱", "咬字", "气息", "连贯", "表现"],
        "mechanism_id": "singing_response_ladder",
        "game_type": "singing_ladder_game",
        "game_name": "歌声闯关梯",
        "operation_mode": "乐句应答 + 表现选择 + 跟唱挑战",
        "visual_metaphor": "乐句阶梯、呼吸气球、声音能量花",
        "feedback": "完成每句后给出咬字、连贯或情绪提示，引导再次演唱。",
        "student_actions": ["选择表现提示", "跟唱乐句", "同伴回应", "再次优化"],
    },
    {
        "rule_id": "creation_to_construction",
        "categories": ["创编实践"],
        "keywords": ["创编", "编创", "即兴", "合作", "小组", "展示", "改编"],
        "mechanism_id": "music_construction_mission",
        "game_type": "creation_mission_game",
        "game_name": "音乐创编工坊",
        "operation_mode": "素材选择 + 拼接改写 + 小组展示",
        "visual_metaphor": "旋律积木、节奏拼图、双声部轨道",
        "feedback": "作品必须满足目标音乐规则，展示时说明使用了哪个要素。",
        "student_actions": ["领取素材", "拼接或改写", "播放检查", "小组展示"],
    },
    {
        "rule_id": "rhythm_rebuild_learning",
        "categories": ["节奏与时值"],
        "keywords": ["节奏拼图", "时值测试", "节奏重建", "全音符", "二分音符", "四分音符"],
        "mechanism_id": "rhythm_rebuild_challenge",
        "game_type": "rhythm_rebuild_challenge",
        "game_name": "节奏重建挑战",
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "operation_mode": "试听目标 + 拖拽重建 + 播放对比 + 拍击迁移",
        "visual_metaphor": "节奏材料卡、挑战区、播放轨道和修正提示",
        "feedback": "反馈指出哪一段时值或拍点不一致，要求学生重听后修正。",
        "student_actions": ["试听目标节奏", "拖拽重建", "播放对比", "拍击或创编迁移"],
    },
    {
        "rule_id": "rhythm_echo_chain_learning",
        "categories": ["节奏与时值"],
        "keywords": ["节奏点按", "节拍闯关", "节奏接龙", "复刻", "跟拍"],
        "mechanism_id": "rhythm_echo_chain",
        "game_type": "rhythm_echo_chain",
        "game_name": "节奏复刻接龙",
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "operation_mode": "听示范 + 复刻拍点 + 接龙延续 + 表现展示",
        "visual_metaphor": "滚动拍点轨道、接龙卡和稳定度反馈条",
        "feedback": "反馈节拍是否稳定，并提示从慢速重新复刻。",
        "student_actions": ["听示范", "复刻拍点", "接龙延续", "稳定表现"],
    },
    {
        "rule_id": "pitch_ladder_learning",
        "categories": ["旋律与音高"],
        "keywords": ["高低选位", "音阶游戏", "音高定位", "唱名", "音阶"],
        "mechanism_id": "pitch_ladder_game",
        "game_type": "pitch_ladder_game",
        "game_name": "音高台阶定位",
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "operation_mode": "试听音列 + 音高定位 + 播放验证 + 模唱迁移",
        "visual_metaphor": "音高台阶、唱名卡和目标音列轨道",
        "feedback": "反馈必须指出具体唱名或音级，不能只说上行下行。",
        "student_actions": ["试听目标音列", "定位唱名", "试听自己的排列", "模唱迁移"],
    },
    {
        "rule_id": "notation_match_learning",
        "categories": ["节奏与时值", "旋律与音高"],
        "keywords": ["音符配对", "符号速认", "谱线寻踪", "乐理", "五线谱"],
        "mechanism_id": "notation_match_lab",
        "game_type": "notation_match_lab",
        "game_name": "乐理证据配对",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "operation_mode": "符号识别 + 名称/声音匹配 + 读谱应用",
        "visual_metaphor": "符号卡、名称卡、声音按钮和小谱例",
        "feedback": "反馈要连接符号、名称和声音用途，不能只判对错。",
        "student_actions": ["观察符号", "匹配名称或声音", "播放验证", "应用到读谱"],
    },
    {
        "rule_id": "segment_ordering_learning",
        "categories": ["歌词与音乐形象", "创编实践"],
        "keywords": ["片段拼接", "乐段重组", "乐句拼图", "曲式", "乐段", "乐句"],
        "mechanism_id": "segment_ordering_studio",
        "game_type": "segment_ordering_studio",
        "game_name": "乐段结构重建",
        "activity_fit": ["listening", "creation"],
        "preferred_activity": "listening",
        "operation_mode": "试听片段 + 拖拽排序 + 整段播放 + 结构说明",
        "visual_metaphor": "乐句积木、段落轨道和结构地图",
        "feedback": "反馈指出开头、发展、重复、对比或收束关系。",
        "student_actions": ["试听片段", "拖拽排序", "播放完整结构", "说明曲式依据"],
    },
    {
        "rule_id": "constrained_composition_learning",
        "categories": ["创编实践", "调式与民族风格"],
        "keywords": ["随心编曲", "约束创编", "乐段重组", "编曲", "小曲"],
        "mechanism_id": "constrained_composition_lab",
        "game_type": "constrained_composition_lab",
        "game_name": "约束创编工坊",
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "operation_mode": "选择本课材料 + 约束拼接 + 试听修正 + 展示说明",
        "visual_metaphor": "旋律积木、节奏卡和作品轨道",
        "feedback": "作品必须使用本课音乐材料，反馈指出是否符合调式、节奏或结构约束。",
        "student_actions": ["选择本课材料", "拼成短句或乐段", "试听修改", "展示说明"],
    },
]

LESSON_MIDDLE_LAYER_STANDARD = {
    "version": "lesson_middle_layer_v1",
    "purpose": "把一份完整音乐教案转换为“整课目标-环节任务-可游戏化点”的稳定结构，供游戏方案、页面生成、OpenCode 修改和质量验收共同使用。",
    "required_fields": [
        "lesson_profile",
        "whole_class_goals",
        "prompt_chain",
        "segment_card_schema",
        "musical_game_logic_contract",
        "lesson_segments",
        "goal_task_game_mapping",
        "selected_game_segment",
        "selection_rules",
        "music_element_mechanic_rules",
        "transfer_payload",
        "quality_gates",
        "decision_trace",
    ],
    "field_notes": {
        "lesson_profile": "课题、学段、课型、整课聚焦音乐要素与流程关键词。",
        "whole_class_goals": "整节课目标、辅助目标与教学重难点，不把某个单一知识点误当整课。",
        "prompt_chain": "模型生成与修改时必须遵循的思考顺序。",
        "segment_card_schema": "每个教学环节卡的统一字段标准。",
        "musical_game_logic_contract": "保证游戏不是空壳互动，而是有声音证据、音乐操作和课堂迁移的音乐游戏。",
        "lesson_segments": "从教案流程中切出的教学环节，每个环节都带任务类型、音乐焦点和游戏化适配度。",
        "goal_task_game_mapping": "每条目标对应最合适的教学环节和可游戏化点。",
        "selected_game_segment": "最终只选择一个最适合做成主游戏的目标环节。",
        "selection_rules": "判定哪个环节最适合做游戏的评分规则。",
        "music_element_mechanic_rules": "音乐要素到游戏机制的映射规则。",
        "transfer_payload": "给后续生成器使用的压缩载荷，避免下游重新猜测课例重点。",
        "quality_gates": "判断这个教案是否已经具备生成课堂音乐游戏的最低信息。",
        "decision_trace": "保留智能体为什么这样选，便于用户确认和继续修改。",
    },
    "segment_task_types": TASK_TYPE_GAMEABLE_POINTS,
    "selection_weights": SEGMENT_SELECTION_WEIGHTS,
    "prompt_chain": LESSON_PROMPT_CHAIN,
    "segment_card_schema": STANDARD_SEGMENT_CARD_SCHEMA,
    "musical_game_logic_contract": MUSICAL_GAME_LOGIC_CONTRACT,
    "music_element_mechanic_rules": MUSIC_ELEMENT_MECHANIC_RULES,
    "quality_gate_notes": {
        "has_primary_goal": "必须能提炼整课目标。",
        "has_selected_segment": "必须能选出一个主游戏环节。",
        "has_music_focus": "必须锁定具体音乐要素或音乐能力。",
        "has_goal_task_mapping": "必须建立目标与环节的对应关系。",
        "has_gameable_point": "必须说明为什么这个环节能转成小游戏。",
    },
}

SPECIFIC_MUSIC_FOCUS_PATTERNS = [
    {
        "pattern": r"(sol|mi|so|5音|3音|唱名|音高特点|高低音)",
        "element": "sol-mi 音高关系",
        "category": "旋律与音高",
        "game_type": "sol_mi_pitch_game",
        "game_name": "sol-mi 音高台阶",
        "mechanic": "把 sol 和 mi 做成两个具体唱名台阶，学生先听目标音列，再拖拽 sol / mi 唱名卡还原旋律，播放后跟琴模唱验证。",
        "rules": ["sol 是较高的具体音，mi 是较低的具体音。", "只能使用 sol 和 mi 两种唱名卡完成音列。", "每次摆放后都要播放并模唱验证，不能只凭文字猜。"],
        "student_actions": ["听辨 sol 和 mi", "拖拽 sol/mi 唱名卡", "播放验证", "跟琴模唱"],
        "win_condition": "学生能听辨并演唱 sol 和 mi 的高低关系。",
    },
    {
        "pattern": r"(f和p|p和f|f\s*/\s*p|强音|弱音|声音强弱|强弱变化|力度记号)",
        "element": "f/p 力度强弱",
        "category": "力度与速度",
        "game_type": "dynamic_contrast_game",
        "game_name": "强弱声音调色盘",
        "mechanic": "把 f 和 p 做成强弱声音按钮与动作卡，学生先听声音强弱，再选择对应力度记号和肢体动作，播放时音量与动作幅度同步变化。",
        "rules": ["f 表示强，动作更大、声音更有力。", "p 表示弱，动作更轻、声音更柔和。", "每次选择都要用听到的声音强弱说明理由。"],
        "student_actions": ["听辨强弱", "选择 f 或 p", "匹配动作幅度", "用动作表现力度"],
        "win_condition": "学生能区分 f 与 p，并用合适动作表现声音强弱。",
    },
    {
        "pattern": r"(三拍子|3/4|四三拍|强弱弱|圆舞曲)",
        "element": "三拍子强弱规律",
        "category": "节奏与时值",
        "game_type": "meter_orbit_game",
        "game_name": "三拍子星球轨道",
        "mechanic": "把“强、弱、弱”三个拍点做成轨道格，学生拖拽月亮、小船或脚步角色进入正确拍位，播放时角色按三拍子律动依次移动。",
        "rules": ["每小节必须放入 1 个强拍和 2 个弱拍。", "强拍角色走得更稳，弱拍角色轻轻摇摆。", "连续排对 2 小节后解锁表演挑战。"],
        "student_actions": ["拖拽强弱拍角色", "点击播放检验三拍子摇荡感", "跟随角色做身体律动", "说出为什么第一拍更强"],
        "win_condition": "学生能正确排出强弱弱，并跟随播放完成稳定的三拍子律动。",
    },
    {
        "pattern": r"(二拍子|2/4|四二拍|强弱交替)",
        "element": "二拍子强弱规律",
        "category": "节奏与时值",
        "game_type": "meter_gate_game",
        "game_name": "强弱节拍门",
        "mechanic": "把每小节做成“强门、弱门”，学生为节奏角色选择正确入口，播放时角色按强弱交替通过。",
        "rules": ["每小节先经过强门，再经过弱门。", "强拍动作更大，弱拍动作更轻。", "排错时节拍门会提示重新听一遍。"],
        "student_actions": ["选择强弱拍入口", "点击播放验证", "用拍手或踏步同步表现"],
        "win_condition": "学生能区分强拍和弱拍，并用动作稳定表现二拍子。",
    },
    {
        "pattern": r"(附点|附点四分|附点节奏)",
        "element": "附点节奏",
        "category": "节奏与时值",
        "game_type": "dotted_rhythm_bounce",
        "game_name": "附点弹跳挑战",
        "mechanic": "把附点节奏做成长短不等的跳台，学生拖拽长跳、短跳角色排列节奏，播放时角色按时值弹跳。",
        "rules": ["附点音符占更长时间，后面的短音快速接上。", "角色必须按“长一点、短一点”的弹跳关系排列。", "播放时如果弹跳不连贯，需要重新调整。"],
        "student_actions": ["拖拽长短节奏卡", "点击播放听弹跳节奏", "跟读或拍击节奏"],
        "win_condition": "学生能听出并排列附点带来的长短对比。",
    },
    {
        "pattern": r"(切分|切分节奏|弱起|重音转移)",
        "element": "切分节奏",
        "category": "节奏与时值",
        "game_type": "syncopation_flag_game",
        "game_name": "切分夺旗",
        "mechanic": "把重音旗帜放在非常规拍位上，学生点击或拖拽旗帜找到切分重音，播放时旗帜随节奏亮起。",
        "rules": ["旗帜不总在第一拍，需要根据听到的重音移动。", "点对重音位置才能继续下一句。", "每次错误后允许重新听。"],
        "student_actions": ["听辨重音", "拖拽旗帜到对应拍位", "跟随播放拍出切分"],
        "win_condition": "学生能指出切分节奏中的重音变化，并用拍击表现。",
    },
    {
        "pattern": r"(休止符|停顿|空拍|静止)",
        "element": "休止符与停顿",
        "category": "节奏与时值",
        "game_type": "rest_light_game",
        "game_name": "休止符红绿灯",
        "mechanic": "把音符和休止符做成红绿灯路口，学生排列节奏时遇到休止符角色必须停住，播放时画面出现停顿反馈。",
        "rules": ["音符格可以前进，休止符格必须停住。", "停顿时不能拍手，只能保持动作。", "连续完成一条节奏路才算通关。"],
        "student_actions": ["拖拽音符和休止符", "点击播放观察停顿", "用身体动作表现有声和无声"],
        "win_condition": "学生能在节奏中准确保留休止符的无声时值。",
    },
    {
        "pattern": r"(全音符|二分音符|四分音符|八分音符|十六分音符|时值)",
        "element": "音符时值",
        "category": "节奏与时值",
        "game_type": "note_value_race",
        "game_name": "音符时值赛跑",
        "mechanic": "给不同时值分配不同速度的角色，学生拖拽角色组成节奏句，播放时角色按拍值依次跑过屏幕。",
        "rules": ["全音符 4 拍、二分音符 2 拍、四分音符 1 拍。", "一条节奏句需要刚好凑满指定拍数。", "角色跑动时间必须与拍值一致。"],
        "student_actions": ["拖拽时值角色", "凑满小节拍数", "播放观察角色时长", "说明每个角色代表几拍"],
        "win_condition": "学生能根据时值组成完整节奏句，并说出总拍数。",
    },
    {
        "pattern": r"(上行|下行|旋律线|音高走向|高低变化)",
        "element": "旋律上行下行",
        "category": "旋律与音高",
        "game_type": "melody_path_game",
        "game_name": "旋律爬坡路线",
        "mechanic": "把旋律走向变成高低路线，学生在格子中拖拽音高点连成旋律线，播放时小角色沿路线行进。",
        "rules": ["音高升高时路线向上，音高降低时路线向下。", "每个格点只能连接相邻旋律片段。", "路线与听到的旋律一致才能通关。"],
        "student_actions": ["听辨旋律走向", "拖拽音高点", "连成旋律线", "播放验证"],
        "win_condition": "学生能用可视化路线表现旋律的高低走向。",
    },
    {
        "pattern": r"(级进|跳进|大跳|小跳|音程)",
        "element": "级进与跳进",
        "category": "旋律与音高",
        "game_type": "interval_step_game",
        "game_name": "音高跳格探险",
        "mechanic": "把级进做成一步格、跳进做成跨格，学生根据旋律片段选择角色走法，播放后系统反馈是否匹配。",
        "rules": ["相邻音用一步格表示。", "跨度较大的音用跳格表示。", "每句旋律要先判断再移动角色。"],
        "student_actions": ["判断级进或跳进", "选择走格方式", "播放并模唱验证"],
        "win_condition": "学生能辨认旋律中的级进和跳进。",
    },
    {
        "pattern": r"(乐句|重复|对比|问答|呼应)",
        "element": "乐句结构",
        "category": "旋律与音高",
        "game_type": "phrase_pair_game",
        "game_name": "乐句问答配对",
        "mechanic": "把重复、对比或问答乐句做成卡片，学生听后把相互呼应的乐句配对，再按顺序拼回歌曲结构。",
        "rules": ["相同或相似乐句可以配成一组。", "对比乐句要说明哪里不同。", "拼回正确顺序后才能进入演唱挑战。"],
        "student_actions": ["听辨乐句", "拖拽配对", "排序歌曲结构", "说出判断依据"],
        "win_condition": "学生能辨认乐句之间的重复、对比或呼应关系。",
    },
    {
        "pattern": r"(五声|宫商角徵羽|宫调式|商调式|角调式|徵调式|羽调式)",
        "element": "五声音阶与民族调式",
        "category": "调式与民族风格",
        "game_type": "pentatonic_grid_game",
        "game_name": "五声宫格拼图",
        "mechanic": "把宫、商、角、徵、羽做成五个音级格，学生拖拽音级拼出短句，播放后判断是否具有民族风格。",
        "rules": ["只能使用五声音级完成旋律。", "旋律要有起承转合的短句感。", "拼完后需要播放并说出风格特点。"],
        "student_actions": ["选择五声音级", "拼接旋律短句", "播放试听", "分享风格判断"],
        "win_condition": "学生能用五声音级拼出符合课例风格的短旋律。",
    },
    {
        "pattern": r"(音色|乐器|小提琴|长笛|古筝|琵琶|二胡|钢琴|打击乐)",
        "element": "乐器音色",
        "category": "音色听辨",
        "game_type": "timbre_detective_game",
        "game_name": "音色侦探",
        "mechanic": "把乐器声音和角色线索做成侦探卡，学生听辨后把音色卡拖到对应乐器或音乐形象上。",
        "rules": ["先听声音，再选择乐器或音色形象。", "每次选择都要给出一个听辨理由。", "答错可重新听，但会提示关注发声特点。"],
        "student_actions": ["聆听音色片段", "拖拽匹配乐器", "说明音色依据"],
        "win_condition": "学生能根据音色特点匹配乐器或音乐形象。",
    },
    {
        "pattern": r"(力度|强弱|渐强|渐弱|轻声|有力)",
        "element": "力度变化",
        "category": "力度与速度",
        "game_type": "dynamic_slider_game",
        "game_name": "力度调色盘",
        "mechanic": "把力度变化做成颜色和音量滑块，学生拖动强弱曲线匹配音乐情绪，播放时画面随力度变化。",
        "rules": ["力度强时颜色更浓，力度弱时颜色更淡。", "渐强要画出上升曲线，渐弱要画出下降曲线。", "曲线与音乐情绪一致才能通关。"],
        "student_actions": ["听辨力度", "拖动画出强弱变化", "播放验证", "用声音模仿"],
        "win_condition": "学生能用图形和声音表现力度变化。",
    },
    {
        "pattern": r"(速度|快慢|渐快|渐慢|稍快|稍慢)",
        "element": "速度变化",
        "category": "力度与速度",
        "game_type": "tempo_dashboard_game",
        "game_name": "速度仪表盘",
        "mechanic": "把速度做成可调仪表盘，学生根据音乐形象选择合适速度，角色运动会随速度变化。",
        "rules": ["不同速度对应不同角色运动状态。", "速度选择要符合歌曲情绪或音乐形象。", "调整后需要播放并说明理由。"],
        "student_actions": ["选择速度档位", "观察角色运动", "对比快慢效果", "说明音乐理由"],
        "win_condition": "学生能根据音乐形象判断并调整合适速度。",
    },
]


def decode_lesson_upload(filename: str, data: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()
    if not data:
        return ""
    if suffix in SUPPORTED_TEXT_EXTENSIONS:
        return _decode_text(data)
    if suffix == ".docx":
        return _extract_docx_text(data)
    if suffix == ".pdf":
        return _extract_pdf_text(data)

    text = _decode_text(data)
    if _looks_like_text(text):
        return text
    raise ValueError("暂时无法读取这个教案文件。请上传 .docx、.txt、.md，或直接粘贴教案文字。")


def build_lesson_game_need(lesson_text: str, extra_need: str = "") -> tuple[str, dict]:
    cleaned = _normalize_space(lesson_text)
    analysis = analyze_lesson_text(cleaned)
    excerpt = _clip(cleaned, MAX_LESSON_CHARS)
    extra = extra_need.strip() or "无"

    need = f"""上传教案生成音乐小游戏：请根据以下完整音乐课教案，自动设计并生成一个可操作的课堂音乐小游戏网页。

核心要求：
1. 不要要求用户先指定游戏形式，请你主动从教案中选择最适合游戏化的教学环节。
2. 游戏必须服务整节课的课例目标，而不是只抽取一个孤立音乐知识点。
3. 活动类型必须是 music_game，生成结果应是真实可玩的音乐小游戏页面。
4. 游戏需要包含清晰规则、学生操作、即时反馈、胜利条件、重新挑战和课堂分享提示。
5. 不限定教材版本；如果教案出现教材信息，只作为课例背景参考。
6. 视觉风格要适合课堂投屏和学生操作，界面简洁、有层次、有小插图感。

教案分析摘要：
- 课题或曲目：{analysis["song_name"]}
- 学段线索：{analysis["grade_band"]}
- 课型线索：{analysis["lesson_type"]}
- 主要音乐要素：{"、".join(analysis["music_elements"]) or "综合音乐感知"}
- 抓住的具体音乐要素：{analysis["specific_focus"]["element"]}
- 教案依据：{analysis["specific_focus"]["evidence"]}
- 适合游戏化环节：{analysis["game_stage"]}
- 选中的目标环节任务：{analysis.get("selected_game_segment", {}).get("task_summary", "未提炼")}
- 推荐游戏方向：{analysis["recommended_game"]["name"]}
- 具体玩法机制：{analysis["recommended_game"]["mechanic"]}
- 标准化环节卡：{analysis.get("selected_game_segment", {}).get("card_title", "课堂核心环节")}
- 学生操作方式：{analysis.get("selected_game_segment", {}).get("student_operation", "听辨、操作、反馈、表达")}
- 音乐要素映射机制：{analysis.get("selected_game_segment", {}).get("music_element_mechanic", {}).get("mechanism_id", "lesson_mission_loop")}
- 音乐性底线：必须包含“{" -> ".join(MUSICAL_GAME_LOGIC_CONTRACT["loop"])}”闭环
- 必须落实的游戏规则：{"；".join(analysis["recommended_game"]["rules"])}
- 胜利条件：{analysis["recommended_game"]["win_condition"]}
- 提示链顺序：{"；".join(item["name"] for item in LESSON_PROMPT_CHAIN)}
- 整课目标-环节映射：{"；".join(_mapping_line(item) for item in analysis.get("goal_task_game_mapping", [])[:3])}

补充要求：
{extra}

原始教案：
{excerpt}
"""
    return need, analysis


def lesson_middle_layer_standard() -> dict:
    return LESSON_MIDDLE_LAYER_STANDARD


def analyze_lesson_text(lesson_text: str) -> dict:
    text = _normalize_space(lesson_text)
    elements = _rank_music_elements(text)
    title = _infer_song_name(text)
    grade = _infer_grade_band(text)
    lesson_type = _infer_lesson_type(text)
    flow = [word for word in FLOW_KEYWORDS if word in text]
    specific_focus = _infer_specific_focus(text, elements)
    objectives = _extract_section_points(text, ["教学目标", "学习目标", "目标"], fallback=_fallback_objective_points(text, specific_focus["element"]))
    difficulties = _extract_section_points(text, ["教学重点", "重点", "难点", "教学难点"], fallback=_fallback_difficulties(specific_focus["element"]))
    middle_layer = _build_lesson_middle_layer(
        text=text,
        song_name=title,
        grade_band=grade,
        lesson_type=lesson_type,
        objectives=objectives,
        difficulties=difficulties,
        flow=flow,
        specific_focus=specific_focus,
    )
    selected_segment = middle_layer.get("selected_game_segment", {})
    game_stage = selected_segment.get("stage_label") or _infer_game_stage(elements, flow, text, specific_focus)
    recommended_game = _recommend_game(elements, flow, text, specific_focus, selected_segment=selected_segment)
    lesson_context = _build_lesson_context(
        text=text,
        song_name=title,
        grade_band=grade,
        lesson_type=lesson_type,
        objectives=objectives,
        difficulties=difficulties,
        flow=flow,
        game_stage=game_stage,
        specific_focus=specific_focus,
        recommended_game=recommended_game,
        middle_layer=middle_layer,
        selected_segment=selected_segment,
    )

    return {
        "song_name": title,
        "grade_band": grade,
        "lesson_type": lesson_type,
        "music_elements": elements[:4],
        "specific_focus": specific_focus,
        "key_objectives": objectives,
        "key_difficulties": difficulties,
        "lesson_flow": flow[:8],
        "game_stage": game_stage,
        "lesson_middle_layer": middle_layer,
        "goal_task_game_mapping": middle_layer.get("goal_task_game_mapping", []),
        "selected_game_segment": selected_segment,
        "recommended_game": recommended_game,
        "objective_summary": _infer_objective_summary(text, elements),
        "lesson_context": lesson_context,
        "text_length": len(text),
    }


def _extract_docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as docx:
            xml = docx.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError("这个 Word 文件无法读取，请另存为 .docx 后重试，或直接粘贴教案文字。") from exc

    root = ET.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return "\n".join(paragraphs)


def _extract_pdf_text(data: bytes) -> str:
    for module_name in ("pypdf", "PyPDF2"):
        try:
            if module_name == "pypdf":
                from pypdf import PdfReader  # type: ignore
            else:
                from PyPDF2 import PdfReader  # type: ignore

            reader = PdfReader(BytesIO(data))
            pages = [(page.extract_text() or "").strip() for page in reader.pages[:12]]
            text = "\n".join(page for page in pages if page)
            if text:
                return text
        except Exception:
            continue
    raise ValueError("暂时无法读取这个 PDF。请复制 PDF 里的教案文字粘贴进输入框，或上传 .docx/.txt 文件。")


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _looks_like_text(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 20:
        return False
    readable = sum(1 for char in stripped if char.isprintable() or char in "\n\r\t")
    return readable / max(len(stripped), 1) > 0.82


def _normalize_space(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}\n\n……后文已省略，请基于以上主要内容生成。"


def _infer_song_name(text: str) -> str:
    title_matches = re.findall(r"《([^》]{1,36})》", text)
    for title in title_matches:
        if not any(word in title for word in ("标准", "课程", "教材", "评价")):
            return f"《{title.strip()}》"

    patterns = [
        r"(?:课题|歌曲|曲目|欣赏曲|教学内容)[:： ]+([^\n，,。；;]{2,32})",
        r"(?:演唱|欣赏)[:： ]+([^\n，,。；;]{2,32})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "自选课例"


def _infer_grade_band(text: str) -> str:
    grade_match = re.search(r"([一二三四五六七八九1-9]年级)", text)
    if grade_match:
        return grade_match.group(1)
    if "小学低年级" in text:
        return "小学低年级"
    if "小学中年级" in text:
        return "小学中年级"
    if "小学高年级" in text:
        return "小学高年级"
    if "小学" in text:
        return "小学"
    if "初中" in text or "七年级" in text or "八年级" in text or "九年级" in text:
        return "初中"
    if "高中" in text:
        return "高中"
    return "小学"


def _infer_lesson_type(text: str) -> str:
    options = [
        ("唱歌课", ["学唱", "演唱", "歌唱", "歌曲"]),
        ("欣赏课", ["欣赏", "聆听", "听辨"]),
        ("创编课", ["创编", "编创", "即兴", "创造"]),
        ("综合活动课", ["律动", "表演", "合作", "展示"]),
    ]
    scores = [(name, sum(text.count(word) for word in words)) for name, words in options]
    best_name, best_score = max(scores, key=lambda item: item[1])
    return best_name if best_score else "综合音乐课"


def _rank_music_elements(text: str) -> list[str]:
    scored: list[tuple[str, int]] = []
    for element, keywords in MUSIC_ELEMENT_KEYWORDS.items():
        score = sum(text.count(keyword) for keyword in keywords)
        if score:
            scored.append((element, score))
    scored.sort(key=lambda item: item[1], reverse=True)
    return [element for element, _score in scored]


def _infer_game_stage(elements: list[str], flow: list[str], text: str, specific_focus: dict) -> str:
    focus_category = specific_focus.get("category", "")
    if focus_category == "创编实践" or "创编" in flow:
        return "创编与展示环节"
    if focus_category == "节奏与时值" or "律动" in flow or "拍击" in flow or any(element == "节奏与时值" for element in elements):
        return "节奏体验与巩固环节"
    if focus_category in {"音色听辨", "力度与速度"} or "聆听" in flow or "欣赏" in flow or "听辨" in text:
        return "聆听辨析环节"
    if focus_category == "旋律与音高" or "学唱" in flow or "模唱" in flow:
        return "学唱巩固环节"
    return "课堂核心练习环节"


def _infer_specific_focus(text: str, elements: list[str]) -> dict:
    candidates: list[tuple[int, int, dict, re.Match[str]]] = []
    for order, focus in enumerate(SPECIFIC_MUSIC_FOCUS_PATTERNS):
        for match in re.finditer(focus["pattern"], text, flags=re.IGNORECASE):
            candidates.append((_focus_match_score(text, match, focus), -order, focus, match))

    if candidates:
        _score, _order, focus, match = max(candidates, key=lambda item: (item[0], item[1]))
        return {
            **focus,
            "evidence": _find_evidence(text, match.group(0)),
            "focus_score": _score,
            "focus_source": _focus_source_label(text, match),
        }

    category = elements[0] if elements else "综合音乐感知"
    fallback_map = {
        "节奏与时值": "节奏型与稳定拍",
        "旋律与音高": "旋律走向",
        "音色听辨": "乐器音色",
        "力度与速度": "音乐表现变化",
        "调式与民族风格": "民族调式风格",
        "歌词与音乐形象": "音乐形象与情绪",
        "演唱表现": "声音表现与连贯歌唱",
        "创编实践": "音乐素材创编",
    }
    element = fallback_map.get(category, "综合音乐感知")
    return {
        "pattern": "",
        "element": element,
        "category": category,
        "game_type": "",
        "game_name": "",
        "mechanic": "",
        "rules": [],
        "student_actions": [],
        "win_condition": "",
        "evidence": _find_evidence(text, element) or "教案中出现多个音乐活动线索，需要围绕最主要的课堂目标设计游戏。",
        "focus_score": 0,
        "focus_source": "fallback",
    }


def _focus_match_score(text: str, match: re.Match[str], focus: dict) -> int:
    start = match.start()
    sentence = _sentence_around(text, start)
    context = text[max(0, start - 80) : min(len(text), match.end() + 80)]
    score = 20

    if any(label in context for label in ["教学重点", "重点", "教学难点", "难点"]):
        score += 90
    if any(label in context for label in ["教学目标", "学习目标", "目标"]):
        score += 60
    if any(label in context for label in ["教学过程", "活动过程", "教学环节"]):
        score += 20
    if any(label in sentence for label in ["认识", "感知", "听辨", "表现", "演唱", "模唱", "创编"]):
        score += 18
    if any(label in sentence for label in ["导入", "复习", "评价", "小结"]) and not any(label in sentence for label in ["重点", "难点", "目标"]):
        score -= 12
    if focus.get("element") in sentence:
        score += 10
    return score


def _focus_source_label(text: str, match: re.Match[str]) -> str:
    context = text[max(0, match.start() - 80) : min(len(text), match.end() + 80)]
    if any(label in context for label in ["教学重点", "重点", "教学难点", "难点"]):
        return "key_difficulty"
    if any(label in context for label in ["教学目标", "学习目标", "目标"]):
        return "objective"
    if any(label in context for label in ["教学过程", "活动过程", "教学环节"]):
        return "lesson_process"
    return "full_text"


def _sentence_around(text: str, index: int) -> str:
    left = max(text.rfind(mark, 0, index) for mark in ["\n", "。", "；", ";", "！", "？"])
    right_candidates = [text.find(mark, index) for mark in ["\n", "。", "；", ";", "！", "？"]]
    right = min([pos for pos in right_candidates if pos >= 0], default=len(text))
    return text[left + 1 : right].strip()


def _find_evidence(text: str, keyword: str) -> str:
    sentences = [part.strip() for part in re.split(r"[\n。；;！？!?]", text) if part.strip()]
    for sentence in sentences:
        if keyword and keyword in sentence:
            return _clip(sentence, 90)
    for sentence in sentences:
        if any(word in sentence for word in ("教学目标", "教学重点", "教学难点", "教学过程", "活动")):
            return _clip(sentence, 90)
    return _clip(text, 90)


def _extract_section_points(text: str, labels: list[str], fallback: list[str]) -> list[str]:
    sentences = [part.strip() for part in re.split(r"[\n。；;！？!?]", text) if part.strip()]
    points: list[str] = []
    for sentence in sentences:
        matched_label = next((label for label in labels if label in sentence), "")
        if matched_label:
            cleaned = sentence
            if "：" in cleaned or ":" in cleaned:
                cleaned = re.split(r"[：:]", cleaned, maxsplit=1)[-1]
            else:
                cleaned = cleaned.split(matched_label, 1)[-1]
            cleaned = cleaned.strip(" ：:-")
            parts = [
                part.strip(" 1234567890一二三四五六七八九十、.．)")
                for part in re.split(r"[；;，,]", cleaned)
                if len(part.strip()) >= 4
            ]
            points.extend(parts[:4])
    return _unique_list(points)[:4] or fallback


def _fallback_objective_points(text: str, music_element: str) -> list[str]:
    points = [
        f"围绕“{music_element}”完成听辨、表现或操作任务。",
        "能在课堂活动中说出自己的音乐判断依据。",
    ]
    if "合作" in text or "小组" in text:
        points.append("在小组合作中完成挑战并展示结果。")
    return points


def _fallback_difficulties(music_element: str) -> list[str]:
    return [
        f"学生容易只停留在表面操作，没有真正理解“{music_element}”。",
        "需要把游戏结果重新带回课堂表达和评价。",
    ]


def _build_lesson_middle_layer(
    *,
    text: str,
    song_name: str,
    grade_band: str,
    lesson_type: str,
    objectives: list[str],
    difficulties: list[str],
    flow: list[str],
    specific_focus: dict,
) -> dict:
    segments = _extract_lesson_segments(text, objectives, specific_focus)
    goal_mapping = _build_goal_task_game_mapping(objectives, segments, specific_focus)
    selected_segment = _select_primary_game_segment(segments, goal_mapping, specific_focus)
    transfer_payload = _build_transfer_payload(
        song_name=song_name,
        grade_band=grade_band,
        lesson_type=lesson_type,
        objectives=objectives,
        specific_focus=specific_focus,
        selected_segment=selected_segment,
        goal_mapping=goal_mapping,
    )
    quality_gates = _build_quality_gates(
        objectives=objectives,
        selected_segment=selected_segment,
        specific_focus=specific_focus,
        goal_mapping=goal_mapping,
    )
    decision_trace = _build_decision_trace(selected_segment, specific_focus, goal_mapping)
    return {
        "standard_version": "lesson_middle_layer_v1",
        "standard": LESSON_MIDDLE_LAYER_STANDARD,
        "lesson_profile": {
            "song_name": song_name,
            "grade_band": grade_band,
            "lesson_type": lesson_type,
            "whole_class_focus": specific_focus.get("element", "综合音乐感知"),
            "flow_keywords": flow[:8],
        },
        "whole_class_goals": {
            "primary_goal": objectives[0] if objectives else f"围绕“{specific_focus.get('element', '综合音乐感知')}”完成本课学习任务。",
            "supporting_goals": objectives[1:4],
            "difficulties": difficulties[:4],
        },
        "prompt_chain": LESSON_PROMPT_CHAIN,
        "segment_card_schema": STANDARD_SEGMENT_CARD_SCHEMA,
        "musical_game_logic_contract": MUSICAL_GAME_LOGIC_CONTRACT,
        "mapping_rules": MIDDLE_LAYER_RULES,
        "selection_rules": {
            "weights": SEGMENT_SELECTION_WEIGHTS,
            "principles": MIDDLE_LAYER_RULES,
            "hard_constraints": [
                "不能选择脱离整课目标的趣味活动。",
                "不能把导入或总结默认做成主游戏。",
                "必须保留至少一个可听、可唱、可拍、可拖拽或可创编的学生动作。",
                "必须能在游戏后回到课堂表达或评价。",
            ],
        },
        "music_element_mechanic_rules": MUSIC_ELEMENT_MECHANIC_RULES,
        "lesson_segments": segments,
        "goal_task_game_mapping": goal_mapping,
        "selected_game_segment": selected_segment,
        "transfer_payload": transfer_payload,
        "quality_gates": quality_gates,
        "decision_trace": decision_trace,
    }


def _extract_lesson_segments(text: str, objectives: list[str], specific_focus: dict) -> list[dict]:
    lines = [line.strip() for line in re.split(r"\n+", text) if line.strip()]
    segments: list[dict] = []
    seen: set[str] = set()

    for line in lines:
        matched_stage = next((keyword for keyword in FLOW_KEYWORDS if keyword in line), "")
        if not matched_stage:
            continue
        if not _looks_like_stage_line(line, matched_stage):
            continue
        normalized_line = line.strip()
        if normalized_line in seen:
            continue
        seen.add(normalized_line)
        segments.append(_segment_from_text(matched_stage, normalized_line, objectives, specific_focus))

    if not segments:
        sentences = [part.strip() for part in re.split(r"[\n。；;！？!?]", text) if part.strip()]
        for sentence in sentences:
            matched_stage = next((keyword for keyword in FLOW_KEYWORDS if keyword in sentence), "")
            if not matched_stage:
                continue
            if not _looks_like_stage_line(sentence, matched_stage):
                continue
            normalized_sentence = sentence.strip()
            if normalized_sentence in seen:
                continue
            seen.add(normalized_sentence)
            segments.append(_segment_from_text(matched_stage, normalized_sentence, objectives, specific_focus))

    if not segments:
        fallback_stage = _fallback_stage_for_focus(specific_focus)
        segments.append(
            _segment_from_text(
                fallback_stage,
                f"{fallback_stage}：围绕“{specific_focus.get('element', '综合音乐感知')}”完成核心任务。",
                objectives,
                specific_focus,
            )
        )

    for index, segment in enumerate(segments, start=1):
        segment["segment_id"] = f"segment_{index}"
        segment["sequence_no"] = index
        segment["is_selected"] = False
    return segments


def _segment_from_text(stage_label: str, raw_text: str, objectives: list[str], specific_focus: dict) -> dict:
    task_type = STAGE_TASK_TYPE_MAP.get(stage_label, "collaborative_task")
    task_summary = _clean_stage_summary(raw_text, stage_label)
    focus = _infer_segment_focus(raw_text, specific_focus)
    objective_links = _linked_objectives_for_segment(objectives, raw_text, focus)
    mechanic = _mechanic_for_segment(focus, task_type, specific_focus)
    score_breakdown = _segment_score_breakdown(stage_label, task_type, raw_text, focus, objective_links, mechanic)
    gameability_score = _segment_gameability_score(stage_label, task_type, raw_text, focus, objective_links, mechanic)
    return {
        "card_schema_version": STANDARD_SEGMENT_CARD_SCHEMA["version"],
        "card_title": f"{stage_label} · {TASK_TYPE_LABELS.get(task_type, '课堂任务')}",
        "stage_label": f"{stage_label}环节",
        "stage_key": stage_label,
        "task_type": task_type,
        "task_type_label": TASK_TYPE_LABELS.get(task_type, "课堂任务"),
        "task_summary": task_summary,
        "raw_excerpt": _clip(raw_text, 90),
        "music_focus": focus,
        "objective_links": objective_links,
        "student_operation": mechanic.get("operation_mode", _student_operation_for_task(task_type)),
        "gameable_point": TASK_TYPE_GAMEABLE_POINTS.get(task_type, "适合转成学生可直接操作的小游戏任务。"),
        "music_element_mechanic": mechanic,
        "recommended_mechanic": _segment_mechanic_hint(task_type, focus, mechanic),
        "score_breakdown": score_breakdown,
        "gameability_score": gameability_score,
        "selection_reason": _segment_selection_reason(stage_label, focus, objective_links, gameability_score),
    }


def _build_goal_task_game_mapping(objectives: list[str], segments: list[dict], specific_focus: dict) -> list[dict]:
    mappings: list[dict] = []
    focus = specific_focus.get("element", "综合音乐感知")
    for objective in objectives[:4]:
        ranked = sorted(
            segments,
            key=lambda segment: _objective_segment_score(objective, segment, focus),
            reverse=True,
        )
        best = ranked[0] if ranked else {}
        mappings.append(
            {
                "goal": objective,
                "best_stage": best.get("stage_label", "课堂核心环节"),
                "task_summary": best.get("task_summary", f"围绕“{focus}”完成课堂任务。"),
                "music_focus": best.get("music_focus", focus),
                "gameable_point": best.get("gameable_point", "适合转成可操作小游戏任务。"),
                "gameability_score": best.get("gameability_score", 60),
                "recommended_mechanic": best.get("recommended_mechanic", "使用拖拽、选择、排序或跟拍互动。"),
                "music_element_mechanic": best.get("music_element_mechanic", {}),
                "score_breakdown": best.get("score_breakdown", {}),
            }
        )
    return mappings


def _select_primary_game_segment(segments: list[dict], goal_mapping: list[dict], specific_focus: dict) -> dict:
    if not segments:
        return {}
    mapped_stages = {item.get("best_stage", "") for item in goal_mapping}
    focus = specific_focus.get("element", "综合音乐感知")
    ranked = sorted(
        segments,
        key=lambda segment: _segment_selection_total(segment, mapped_stages, focus),
        reverse=True,
    )
    for rank, segment in enumerate(ranked, start=1):
        segment["selection_rank"] = rank
        segment["selection_total"] = _segment_selection_total(segment, mapped_stages, focus)
    selected = dict(_prefer_segment_for_focus(ranked, focus))
    selected["is_selected"] = True
    for segment in segments:
        segment["is_selected"] = segment.get("segment_id") == selected.get("segment_id")
    return selected


def _prefer_segment_for_focus(ranked_segments: list[dict], focus: str) -> dict:
    if not ranked_segments:
        return {}
    best = ranked_segments[0]
    best_total = int(best.get("selection_total", 0))

    preferred_task_types: set[str] = set()
    if any(token in focus for token in ["sol", "mi", "音高", "旋律", "级进", "跳进"]):
        preferred_task_types = {"sing_practice"}
    elif any(token in focus for token in ["f/p", "力度", "强弱", "音色", "乐器"]):
        preferred_task_types = {"listen_discriminate", "rhythm_perform"}
    elif any(token in focus for token in ["节奏", "拍", "切分", "附点", "休止符"]):
        preferred_task_types = {"rhythm_perform"}
    elif any(token in focus for token in ["创编", "调式", "五声"]):
        preferred_task_types = {"creative_construction"}

    if not preferred_task_types:
        return best

    for segment in ranked_segments:
        if segment.get("task_type") in preferred_task_types and best_total - int(segment.get("selection_total", 0)) <= 10:
            return segment
    return best


def _build_transfer_payload(
    *,
    song_name: str,
    grade_band: str,
    lesson_type: str,
    objectives: list[str],
    specific_focus: dict,
    selected_segment: dict,
    goal_mapping: list[dict],
) -> dict:
    focus = specific_focus.get("element", "综合音乐感知")
    preferred_mechanic = str(
        specific_focus.get("mechanic")
        or selected_segment.get("recommended_mechanic", "")
    ).strip()
    linked_objective = ""
    objective_links = selected_segment.get("objective_links", [])
    if isinstance(objective_links, list) and objective_links:
        linked_objective = str(objective_links[0])
    return {
        "song_name": song_name,
        "grade_band": grade_band,
        "lesson_type": lesson_type,
        "target_stage": selected_segment.get("stage_label", "课堂核心练习环节"),
        "target_objective": linked_objective or (objectives[0] if objectives else f"围绕“{focus}”完成本课核心体验与表达。"),
        "target_music_element": selected_segment.get("music_focus") or focus,
        "target_segment_task": _focus_aligned_task_summary(selected_segment.get("task_summary", ""), selected_segment.get("music_focus") or focus),
        "target_segment_type": selected_segment.get("task_type", ""),
        "target_segment_gameable_point": selected_segment.get("gameable_point", ""),
        "recommended_mechanic": preferred_mechanic,
        "music_element_mechanic": selected_segment.get("music_element_mechanic", {}),
        "student_operation": selected_segment.get("student_operation", ""),
        "selection_reason": selected_segment.get("selection_reason", ""),
        "selection_score": selected_segment.get("selection_total", selected_segment.get("gameability_score", 0)),
        "prompt_chain_summary": [
            f"{item['name']}：{item['instruction']}"
            for item in LESSON_PROMPT_CHAIN
        ],
        "goal_task_mapping_summary": [_mapping_line(item) for item in goal_mapping[:3]],
    }


def _focus_aligned_task_summary(task_summary: str, focus: str) -> str:
    task = str(task_summary or "").strip().rstrip("。；;，,")
    focus_text = str(focus or "").strip()
    if not task:
        return f"围绕“{focus_text or '综合音乐感知'}”完成核心任务。"
    if focus_text and not _text_overlap(task, focus_text):
        return f"{task}，重点解决“{focus_text}”。"
    return task


def _build_quality_gates(
    *,
    objectives: list[str],
    selected_segment: dict,
    specific_focus: dict,
    goal_mapping: list[dict],
) -> dict:
    focus = specific_focus.get("element", "")
    return {
        "has_primary_goal": bool(objectives),
        "has_selected_segment": bool(selected_segment.get("stage_label")),
        "has_music_focus": bool(focus and focus != "综合音乐感知"),
        "has_goal_task_mapping": bool(goal_mapping),
        "has_gameable_point": bool(selected_segment.get("gameable_point")),
        "has_mechanic_mapping": bool(selected_segment.get("music_element_mechanic", {}).get("mechanism_id")),
    }


def _build_decision_trace(selected_segment: dict, specific_focus: dict, goal_mapping: list[dict]) -> list[str]:
    trace: list[str] = []
    focus = specific_focus.get("element", "综合音乐感知")
    evidence = specific_focus.get("evidence", "")
    if focus:
        trace.append(f"先从教案中锁定“{focus}”作为本轮游戏要服务的音乐理解点。")
    if evidence:
        trace.append(f"依据句：{evidence}")
    if selected_segment.get("stage_label"):
        trace.append(
            f"选择{selected_segment.get('stage_label')}，因为该环节任务是“{selected_segment.get('task_summary', '课堂核心任务')}”。"
        )
    if selected_segment.get("gameable_point"):
        trace.append(f"游戏化理由：{selected_segment.get('gameable_point')}")
    if goal_mapping:
        trace.append(f"目标对应：{_mapping_line(goal_mapping[0])}")
    return trace[:5]


def _clean_stage_summary(text: str, stage_label: str) -> str:
    cleaned = text
    if "：" in cleaned or ":" in cleaned:
        cleaned = re.split(r"[：:]", cleaned, maxsplit=1)[-1]
    cleaned = cleaned.replace(stage_label, "", 1).strip(" ：:-")
    return cleaned or f"围绕“{stage_label}”开展课堂任务。"


def _looks_like_stage_line(text: str, stage_label: str) -> bool:
    stripped = text.strip()
    if re.match(rf"^(?:\d+[.、]|\(?[一二三四五六七八九十]+\)?[.、]?)?\s*{re.escape(stage_label)}[：: ]", stripped):
        return True
    if stripped.startswith(stage_label):
        return True
    if any(label in stripped for label in ["教学目标", "学习目标", "教学重点", "教学难点", "课题", "歌曲", "曲目"]):
        return False
    return any(marker in stripped for marker in ["教学过程", "活动", "环节"])


def _infer_segment_focus(text: str, specific_focus: dict) -> str:
    focus = specific_focus.get("element", "综合音乐感知")
    keywords = [token for token in re.split(r"[与、]", focus) if token]
    if any(keyword in text for keyword in keywords):
        return focus
    for category, words in MUSIC_ELEMENT_KEYWORDS.items():
        if any(word in text for word in words):
            return specific_focus.get("element") if category == specific_focus.get("category") else category
    return focus


def _linked_objectives_for_segment(objectives: list[str], text: str, focus: str) -> list[str]:
    linked = [
        objective
        for objective in objectives
        if _text_overlap(objective, text) or _text_overlap(objective, focus)
    ]
    if linked:
        return linked[:2]
    return objectives[:1]


def _segment_score_breakdown(
    stage_label: str,
    task_type: str,
    text: str,
    focus: str,
    objective_links: list[str],
    mechanic: dict,
) -> dict:
    objective_alignment = SEGMENT_SELECTION_WEIGHTS["objective_alignment"] if objective_links else 8
    music_focus_alignment = SEGMENT_SELECTION_WEIGHTS["music_focus_alignment"] if focus and focus != "综合音乐感知" else 10
    if focus and _text_overlap(text, focus):
        music_focus_alignment = min(SEGMENT_SELECTION_WEIGHTS["music_focus_alignment"], music_focus_alignment + 4)

    student_operation = 8
    if task_type in {"listen_discriminate", "sing_practice", "rhythm_perform", "creative_construction", "collaborative_task"}:
        student_operation = 14
    if any(word in text for word in ["拖拽", "点击", "排序", "匹配", "拍击", "模仿", "律动", "演唱", "选择", "连接"]):
        student_operation = SEGMENT_SELECTION_WEIGHTS["student_operation"]

    feedback_visibility = 10
    if any(word in text for word in ["听", "播放", "反馈", "评价", "展示", "检查", "判断", "验证"]):
        feedback_visibility = SEGMENT_SELECTION_WEIGHTS["feedback_visibility"]
    elif mechanic.get("feedback"):
        feedback_visibility = 14

    classroom_position = 8
    if task_type in {"listen_discriminate", "sing_practice", "rhythm_perform", "creative_construction"}:
        classroom_position = SEGMENT_SELECTION_WEIGHTS["classroom_position"]
    if stage_label in {"导入", "评价"} or task_type == "showcase_reflection":
        classroom_position = 3

    return {
        "objective_alignment": objective_alignment,
        "music_focus_alignment": music_focus_alignment,
        "student_operation": student_operation,
        "feedback_visibility": feedback_visibility,
        "classroom_position": classroom_position,
    }


def _segment_gameability_score(
    stage_label: str,
    task_type: str,
    text: str,
    focus: str,
    objective_links: list[str],
    mechanic: dict | None = None,
) -> int:
    mechanic = mechanic or _mechanic_for_segment(focus, task_type, {})
    breakdown = _segment_score_breakdown(stage_label, task_type, text, focus, objective_links, mechanic)
    score = sum(int(value) for value in breakdown.values())
    if any(word in text for word in ["游戏", "挑战", "任务", "练习", "闯关"]):
        score += 4
    score += _focus_task_affinity(focus, task_type)
    if stage_label in {"导入", "评价"}:
        score -= 10
    if task_type == "showcase_reflection":
        score -= 6
    return max(35, min(score, 96))


def _segment_selection_total(segment: dict, mapped_stages: set[str], focus: str) -> int:
    return (
        int(segment.get("gameability_score", 0))
        + (10 if segment.get("stage_label") in mapped_stages else 0)
        + (8 if segment.get("music_focus") == focus else 0)
        + _focus_task_affinity(focus, str(segment.get("task_type", "")))
    )


def _focus_task_affinity(focus: str, task_type: str) -> int:
    if any(token in focus for token in ["sol", "mi", "音高", "旋律", "级进", "跳进"]):
        if task_type == "sing_practice":
            return 14
        if task_type == "listen_discriminate":
            return 6
    if any(token in focus for token in ["f/p", "力度", "强弱"]):
        if task_type in {"listen_discriminate", "rhythm_perform"}:
            return 12
        if task_type == "sing_practice":
            return 5
    if any(token in focus for token in ["节奏", "拍", "切分", "附点", "休止符"]):
        if task_type == "rhythm_perform":
            return 14
        if task_type == "listen_discriminate":
            return 6
    if "乐句" in focus:
        if task_type in {"sing_practice", "listen_discriminate"}:
            return 10
    if any(token in focus for token in ["音色", "乐器"]):
        return 12 if task_type == "listen_discriminate" else 0
    if any(token in focus for token in ["创编", "调式", "五声"]):
        return 12 if task_type == "creative_construction" else 0
    return 0


def _student_operation_for_task(task_type: str) -> str:
    if task_type == "listen_discriminate":
        return "聆听后选择、匹配或定位。"
    if task_type == "sing_practice":
        return "跟唱、模唱或乐句应答。"
    if task_type == "rhythm_perform":
        return "拍击、拖拽节奏卡或跟随律动。"
    if task_type == "creative_construction":
        return "选择素材、拼接、改写或展示。"
    if task_type == "collaborative_task":
        return "小组接力、轮流操作或合作展示。"
    return "观察、表达或评价。"


def _mechanic_for_segment(focus: str, task_type: str, specific_focus: dict) -> dict:
    specific_name = str(specific_focus.get("game_name") or "")
    if specific_name:
        return {
            "rule_id": "specific_focus_pattern",
            "mechanism_id": specific_focus.get("game_type", "specific_music_game"),
            "game_type": specific_focus.get("game_type", "lesson_mission_game"),
            "game_name": specific_name,
            "operation_mode": _student_operation_for_task(task_type),
            "visual_metaphor": specific_focus.get("mechanic", ""),
            "feedback": specific_focus.get("win_condition", ""),
            "student_actions": specific_focus.get("student_actions", []),
            "source": "specific_focus_patterns",
        }

    for rule in MUSIC_ELEMENT_MECHANIC_RULES:
        if any(category in focus for category in rule["categories"]):
            return {**rule, "source": "music_element_mechanic_rules"}
        if any(keyword and keyword in focus for keyword in rule["keywords"]):
            return {**rule, "source": "music_element_mechanic_rules"}

    fallback_by_task = {
        "listen_discriminate": "timbre_detective_match",
        "sing_practice": "singing_response_ladder",
        "rhythm_perform": "rhythm_drag_playback",
        "creative_construction": "music_construction_mission",
    }
    preferred = fallback_by_task.get(task_type, "music_scene_choice")
    for rule in MUSIC_ELEMENT_MECHANIC_RULES:
        if rule["mechanism_id"] == preferred:
            return {**rule, "source": "task_type_fallback"}

    return {
        "rule_id": "generic_lesson_mission",
        "mechanism_id": "lesson_mission_loop",
        "game_type": "lesson_mission_game",
        "game_name": "课例任务闯关",
        "operation_mode": _student_operation_for_task(task_type),
        "visual_metaphor": "任务卡、进度条和课堂分享卡",
        "feedback": "完成后给出音乐理由提示。",
        "student_actions": ["完成任务", "查看反馈", "分享理由"],
        "source": "generic_fallback",
    }


def _segment_mechanic_hint(task_type: str, focus: str, mechanic: dict | None = None) -> str:
    mechanic = mechanic or _mechanic_for_segment(focus, task_type, {})
    operation = mechanic.get("operation_mode", _student_operation_for_task(task_type))
    feedback = mechanic.get("feedback", "完成后回到课堂表达。")
    if task_type == "listen_discriminate":
        return f"围绕“{focus}”设计{operation}，{feedback}"
    if task_type == "sing_practice":
        return f"围绕“{focus}”设计{operation}，{feedback}"
    if task_type == "rhythm_perform":
        return f"围绕“{focus}”设计{operation}，{feedback}"
    if task_type == "creative_construction":
        return f"围绕“{focus}”设计{operation}，{feedback}"
    if task_type == "collaborative_task":
        return f"围绕“{focus}”设计{operation}，{feedback}"
    return f"围绕“{focus}”保留必要规则，采用{operation}，并在完成后回到课堂表达。"


def _segment_selection_reason(stage_label: str, focus: str, objective_links: list[str], gameability_score: int) -> str:
    linked_goal = objective_links[0] if objective_links else f"围绕“{focus}”完成课堂任务。"
    return f"{stage_label}环节与“{focus}”直接相关，且能承载“{linked_goal}”，游戏化适配度 {gameability_score} 分。"


def _objective_segment_score(objective: str, segment: dict, focus: str) -> int:
    score = int(segment.get("gameability_score", 0))
    if objective in segment.get("objective_links", []):
        score += 18
    if _text_overlap(objective, segment.get("task_summary", "")):
        score += 10
    if _text_overlap(objective, focus) or _text_overlap(segment.get("music_focus", ""), focus):
        score += 8
    return score


def _fallback_stage_for_focus(specific_focus: dict) -> str:
    category = specific_focus.get("category", "")
    if category == "创编实践":
        return "创编"
    if category in {"节奏与时值", "旋律与音高", "演唱表现"}:
        return "律动"
    if category in {"音色听辨", "力度与速度", "调式与民族风格"}:
        return "聆听"
    return "展示"


def _text_overlap(source: str, target: str) -> bool:
    source_text = str(source or "").strip()
    target_text = str(target or "").strip()
    if not source_text or not target_text:
        return False
    if source_text in target_text or target_text in source_text:
        return True
    source_tokens = {token for token in re.split(r"[，,、；;：:\s（）()]+", source_text) if len(token) >= 2}
    target_tokens = {token for token in re.split(r"[，,、；;：:\s（）()]+", target_text) if len(token) >= 2}
    return bool(source_tokens & target_tokens)


def _mapping_line(item: dict) -> str:
    return f"{item.get('goal', '课堂目标')} -> {item.get('best_stage', '课堂核心环节')} -> {item.get('gameable_point', '转成可操作任务')}"


def _build_lesson_context(
    *,
    text: str,
    song_name: str,
    grade_band: str,
    lesson_type: str,
    objectives: list[str],
    difficulties: list[str],
    flow: list[str],
    game_stage: str,
    specific_focus: dict,
    recommended_game: dict,
    middle_layer: dict,
    selected_segment: dict,
) -> dict:
    focus = specific_focus.get("element", "综合音乐感知")
    evidence = specific_focus.get("evidence", "")
    transfer_payload = middle_layer.get("transfer_payload", {})
    selected_objectives = selected_segment.get("objective_links", []) if isinstance(selected_segment.get("objective_links"), list) else []
    target_objective = (
        str(transfer_payload.get("target_objective") or "")
        or (str(selected_objectives[0]) if selected_objectives else "")
        or _choose_target_objective(objectives, focus)
    )
    target_stage = str(transfer_payload.get("target_stage") or game_stage)
    target_segment_task = str(transfer_payload.get("target_segment_task") or selected_segment.get("task_summary") or "")
    target_segment_gameable_point = str(
        transfer_payload.get("target_segment_gameable_point") or selected_segment.get("gameable_point") or ""
    )
    music_element_mechanic = transfer_payload.get("music_element_mechanic") or selected_segment.get("music_element_mechanic", {})
    student_task = _build_student_task(focus, recommended_game)
    teacher_guidance = _build_teacher_guidance(song_name, focus, target_stage, target_objective)
    assessment_closure = _build_assessment_closure(focus, target_objective)
    stage_reason = _build_stage_reason(target_stage, focus, evidence)
    why_fit = _build_fit_reason(song_name, focus, target_stage, target_objective, recommended_game)
    revision_focus = [
        "如果网页互动偏离该环节，要优先改回课例目标。",
        f"如果玩法过于通用，要继续强化“{focus}”的音乐判断。",
        "如果页面只好玩不好教，要补上教师引导语和课堂收束。",
    ]

    return {
        "song_name": song_name,
        "grade_band": grade_band,
        "lesson_type": lesson_type,
        "lesson_objectives": objectives,
        "lesson_difficulties": difficulties,
        "teaching_flow": flow[:8],
        "middle_layer_standard_version": middle_layer.get("standard_version", "lesson_middle_layer_v1"),
        "middle_layer_schema": LESSON_MIDDLE_LAYER_STANDARD,
        "prompt_chain": LESSON_PROMPT_CHAIN,
        "segment_card_schema": STANDARD_SEGMENT_CARD_SCHEMA,
        "musical_game_logic_contract": MUSICAL_GAME_LOGIC_CONTRACT,
        "music_element_mechanic_rules": MUSIC_ELEMENT_MECHANIC_RULES,
        "middle_layer_standard": middle_layer,
        "lesson_middle_layer": middle_layer,
        "goal_task_game_mapping": middle_layer.get("goal_task_game_mapping", []),
        "selected_game_segment": selected_segment,
        "decision_trace": middle_layer.get("decision_trace", []),
        "quality_gates": middle_layer.get("quality_gates", {}),
        "transfer_payload": transfer_payload,
        "target_stage": target_stage,
        "target_objective": target_objective,
        "target_music_element": focus,
        "target_segment_task": target_segment_task,
        "target_segment_type": transfer_payload.get("target_segment_type", selected_segment.get("task_type", "")),
        "target_segment_gameable_point": target_segment_gameable_point,
        "target_segment_mechanic": transfer_payload.get("recommended_mechanic", selected_segment.get("recommended_mechanic", "")),
        "music_element_mechanic": music_element_mechanic,
        "student_operation": transfer_payload.get("student_operation", selected_segment.get("student_operation", "")),
        "recommended_game_type": recommended_game.get("type", ""),
        "recommended_game_name": recommended_game.get("name", ""),
        "recommended_game_mechanic": recommended_game.get("mechanic", ""),
        "recommended_game_rules": recommended_game.get("rules", []),
        "recommended_game_actions": recommended_game.get("student_actions", []),
        "lesson_evidence": evidence,
        "stage_reason": stage_reason,
        "student_task": student_task,
        "teacher_guidance": teacher_guidance,
        "assessment_closure": assessment_closure,
        "why_this_game_fits_this_lesson": why_fit,
        "continue_revision_focus": revision_focus,
        "lesson_fit_rubric": [
            "必须服务教案中的目标环节，而不是脱离课堂单独成页。",
            f"必须围绕“{focus}”设计规则、反馈和评价。",
            "必须让学生在游戏后还能回到表达、展示或评价。",
        ],
    }


def _choose_target_objective(objectives: list[str], focus: str) -> str:
    for objective in objectives:
        if focus[:2] in objective or any(word and word in objective for word in re.split(r"[与、]", focus)):
            return objective
    return objectives[0] if objectives else f"围绕“{focus}”完成本课核心体验与表达。"


def _build_student_task(focus: str, recommended_game: dict) -> str:
    actions = recommended_game.get("student_actions") or []
    if actions:
        return "，".join(actions[:3]) + "。"
    return f"学生围绕“{focus}”完成拖拽、听辨、点击或排序挑战，并说出音乐理由。"


def _build_teacher_guidance(song_name: str, focus: str, game_stage: str, target_objective: str) -> list[str]:
    return [
        f"先说明这不是独立小游戏，而是《{song_name}》在“{game_stage}”中的课堂任务。",
        f"引导学生先关注“{focus}”，再进入操作，不要只看角色或动画。",
        f"操作结束后追问：这个结果怎样帮助你完成“{target_objective}”？",
    ]


def _build_assessment_closure(focus: str, target_objective: str) -> str:
    return f"完成游戏后，学生需要用语言、拍击、演唱或动作再次表现“{focus}”，并说明这如何对应“{target_objective}”。"


def _build_stage_reason(game_stage: str, focus: str, evidence: str) -> str:
    return f"该游戏放在“{game_stage}”，因为教案已明确出现“{focus}”相关线索：{evidence}"


def _build_fit_reason(song_name: str, focus: str, game_stage: str, target_objective: str, recommended_game: dict) -> str:
    return (
        f"《{song_name}》这节课不应只生成一个通用小游戏，而应把“{game_stage}”里的“{focus}”转成可操作任务。"
        f" 选择“{recommended_game.get('name', '课例任务闯关')}”是为了让学生通过真实操作达成“{target_objective}”。"
    )


def _unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def _game_from_mechanic_rule(
    mechanic_rule: dict,
    *,
    specific_focus: dict,
    selected_segment: dict,
    segment_summary: str,
    segment_gameable_point: str,
) -> dict:
    focus = specific_focus.get("element") or selected_segment.get("music_focus") or "综合音乐感知"
    game_name = mechanic_rule.get("game_name") or "课例任务闯关"
    operation = mechanic_rule.get("operation_mode", "听辨、操作、反馈、表达")
    feedback = mechanic_rule.get("feedback", "完成后说出音乐判断依据。")
    visual = mechanic_rule.get("visual_metaphor", "任务卡和反馈动画")
    return {
        "type": mechanic_rule.get("game_type", "lesson_mission_game"),
        "name": game_name,
        "music_element": focus,
        "activity_fit": mechanic_rule.get("activity_fit", []),
        "preferred_activity": mechanic_rule.get("preferred_activity", ""),
        "mechanic": (
            f"把“{focus}”转成“{operation}”的课堂小游戏，画面采用{visual}，"
            f"并让学生在操作后获得反馈：{feedback} {segment_gameable_point}"
        ).strip(),
        "reason": (
            f"该机制来自音乐要素映射规则“{mechanic_rule.get('rule_id', 'generic_lesson_mission')}”，"
            f"适合承接环节任务“{segment_summary or selected_segment.get('task_summary', '课堂核心任务')}”。"
        ),
        "rules": _rules_from_mechanic_rule(focus, mechanic_rule, segment_gameable_point),
        "student_actions": mechanic_rule.get("student_actions") or ["完成任务", "播放验证", "说明音乐理由"],
        "win_condition": f"学生完成“{focus}”相关操作后，能用听、唱、拍、演或创编说明自己的音乐判断。",
        "target_segment_task": segment_summary,
        "target_segment_point": segment_gameable_point,
        "music_element_mechanic": mechanic_rule,
        "mechanism_id": mechanic_rule.get("mechanism_id", ""),
    }


def _rules_from_mechanic_rule(focus: str, mechanic_rule: dict, segment_gameable_point: str) -> list[str]:
    operation = mechanic_rule.get("operation_mode", "操作并验证")
    feedback = mechanic_rule.get("feedback", "系统给出反馈。")
    rules = [
        f"每一轮只聚焦“{focus}”，不要混入无关音乐任务。",
        f"学生先完成“{operation}”，再点击播放或查看反馈。",
        feedback,
    ]
    if segment_gameable_point:
        rules.append(segment_gameable_point)
    rules.append("通关后必须说出一个音乐理由，教师再带回课例目标。")
    return rules[:5]


def _recommend_game(elements: list[str], flow: list[str], text: str, specific_focus: dict, *, selected_segment: dict | None = None) -> dict:
    selected_segment = selected_segment or {}
    segment_summary = selected_segment.get("task_summary", "")
    segment_gameable_point = selected_segment.get("gameable_point", "")
    mechanic_rule = selected_segment.get("music_element_mechanic") or _mechanic_for_segment(
        specific_focus.get("element", "综合音乐感知"),
        selected_segment.get("task_type", "collaborative_task"),
        specific_focus,
    )

    if specific_focus.get("game_name"):
        return {
            "type": specific_focus["game_type"],
            "name": specific_focus["game_name"],
            "music_element": specific_focus["element"],
            "mechanic": f"{specific_focus['mechanic']} {segment_gameable_point}".strip(),
            "reason": f"{specific_focus['mechanic']} {segment_summary}".strip(),
            "rules": specific_focus["rules"],
            "student_actions": specific_focus["student_actions"],
            "win_condition": specific_focus["win_condition"],
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
            "music_element_mechanic": mechanic_rule,
            "mechanism_id": mechanic_rule.get("mechanism_id", ""),
        }

    if mechanic_rule:
        return _game_from_mechanic_rule(
            mechanic_rule,
            specific_focus=specific_focus,
            selected_segment=selected_segment,
            segment_summary=segment_summary,
            segment_gameable_point=segment_gameable_point,
        )

    element_set = set(elements)
    if "节奏与时值" in element_set:
        return {
            "type": "rhythm_race_game",
            "name": "节奏任务赛跑",
            "music_element": specific_focus.get("element", "节奏与拍点"),
            "mechanic": f"把教案中的节奏型或拍点变成可拖拽的角色任务，学生排列后播放验证。{segment_gameable_point}".strip(),
            "reason": f"把不同节奏型、时值或拍点变成角色行动规则，学生通过排列和播放来验证节奏句。{segment_summary}".strip(),
            "rules": ["每个角色对应一个节奏单位。", "学生需要凑成完整小节。", "播放后根据节拍反馈调整。"],
            "student_actions": ["拖拽节奏角色", "播放验证", "拍击模仿", "说明节奏理由"],
            "win_condition": "学生能排出符合拍点的节奏句并稳定表现。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    if "旋律与音高" in element_set:
        return {
            "type": "pitch_path_game",
            "name": "旋律路线挑战",
            "music_element": specific_focus.get("element", "旋律走向"),
            "mechanic": f"把旋律高低变成路线格，学生连接音高点后播放验证。{segment_gameable_point}".strip(),
            "reason": f"把音高走向变成可拖拽路线，学生在上行、下行、模唱中完成旋律辨认。{segment_summary}".strip(),
            "rules": ["音高变化要和路线起伏一致。", "每段旋律都要播放验证。", "完成后进行模唱。"],
            "student_actions": ["听辨旋律", "连接路线", "播放验证", "模唱旋律"],
            "win_condition": "学生能用路线表达旋律走向并完成模唱。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    if "音色听辨" in element_set:
        return {
            "type": "timbre_match_game",
            "name": "音色找朋友",
            "music_element": specific_focus.get("element", "音色听辨"),
            "mechanic": f"把音色线索做成乐器卡和形象卡，学生听后拖拽匹配。{segment_gameable_point}".strip(),
            "reason": f"把乐器音色与音乐形象做成听辨匹配，让学生边听边选择并说明依据。{segment_summary}".strip(),
            "rules": ["先听再选，不能只看图猜。", "每次选择要说出音色依据。", "答错后给出听辨提示。"],
            "student_actions": ["聆听音色", "拖拽匹配", "说明依据"],
            "win_condition": "学生能根据音色特点完成匹配。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    if "调式与民族风格" in element_set:
        return {
            "type": "mode_puzzle_game",
            "name": "民族调式拼图",
            "music_element": specific_focus.get("element", "民族调式"),
            "mechanic": f"把调式音级和短句素材做成拼图，学生组合后播放感受风格。{segment_gameable_point}".strip(),
            "reason": f"把调式音级、民族风格和短句素材做成拼图，学生通过组合感受风格特点。{segment_summary}".strip(),
            "rules": ["素材要符合调式音级。", "旋律短句要能播放。", "完成后说出民族风格依据。"],
            "student_actions": ["选择音级", "拼接短句", "播放试听", "分享判断"],
            "win_condition": "学生能拼出有调式风格的短句。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    if "创编实践" in element_set or "创编" in flow:
        return {
            "type": "creation_mission_game",
            "name": "小小作曲任务",
            "music_element": specific_focus.get("element", "音乐素材创编"),
            "mechanic": f"把教案里的创编要求拆成任务卡，学生完成选择、拼接、展示和互评。{segment_gameable_point}".strip(),
            "reason": f"把教案里的创编要求拆成任务卡，学生完成选择、拼接、展示和互评。{segment_summary}".strip(),
            "rules": ["每组先完成一个基础素材。", "再选择变化方式进行创编。", "展示时说明使用了哪个音乐要素。"],
            "student_actions": ["领取任务卡", "拼接素材", "小组展示", "互评优化"],
            "win_condition": "学生能完成与课例目标相关的短小创编。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    if "欣赏" in flow or "聆听" in flow or "情绪" in text:
        return {
            "type": "expression_control_game",
            "name": "音乐表情控制台",
            "music_element": specific_focus.get("element", "音乐情绪与形象"),
            "mechanic": f"把速度、力度、情绪、音乐形象做成控制项，学生用判断结果推动游戏。{segment_gameable_point}".strip(),
            "reason": f"把速度、力度、情绪、音乐形象做成可选择的控制项，学生用判断结果推动游戏。{segment_summary}".strip(),
            "rules": ["先聆听再选择控制项。", "选择要符合音乐形象。", "完成后说出判断依据。"],
            "student_actions": ["聆听音乐", "选择表情控制项", "观察反馈", "说明理由"],
            "win_condition": "学生能根据音乐特点判断情绪或形象。",
            "target_segment_task": segment_summary,
            "target_segment_point": segment_gameable_point,
        }
    return {
        "type": "lesson_mission_game",
        "name": "课例任务闯关",
        "music_element": specific_focus.get("element", "综合音乐感知"),
        "mechanic": f"把教案核心目标拆成可操作任务，学生在挑战、反馈和分享中完成学习闭环。{segment_gameable_point}".strip(),
        "reason": f"把教案核心目标拆成可操作任务，学生在挑战、反馈和分享中完成学习闭环。{segment_summary}".strip(),
        "rules": ["每一关只聚焦一个音乐任务。", "完成后获得即时反馈。", "最后需要课堂分享。"],
        "student_actions": ["选择任务", "完成挑战", "查看反馈", "分享总结"],
        "win_condition": "学生能完成教案核心目标对应的课堂任务。",
        "target_segment_task": segment_summary,
        "target_segment_point": segment_gameable_point,
    }


def _infer_objective_summary(text: str, elements: list[str]) -> str:
    objective_match = re.search(r"(?:教学目标|学习目标|目标)[:：\n ]+(.{20,180})", text)
    if objective_match:
        return _normalize_space(objective_match.group(1))
    if elements:
        return f"围绕{elements[0]}开展感知、体验和表现。"
    return "围绕课例核心内容开展音乐感知、表现和合作学习。"
