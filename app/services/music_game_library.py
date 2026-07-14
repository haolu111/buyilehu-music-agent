from __future__ import annotations

from typing import Any


PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

LEGACY_TO_PRODUCTION_TEMPLATE_IDS = {
    "rhythm_echo_chain": "rhythm_echo_core",
    "rhythm_rebuild_challenge": "composition_puzzle_core",
    "constrained_composition_lab": "composition_puzzle_core",
    "composition_puzzle_game": "composition_puzzle_core",
    "melody_rhythm_puzzle": "composition_puzzle_core",
    "pitch_ladder_game": "pitch_ladder_core",
    "sol_mi_pitch_game": "pitch_ladder_core",
    "solmi_pitch_ladder": "pitch_ladder_core",
    "melody_path_game": "pitch_ladder_core",
    "pitch_flying_game": "pitch_ladder_core",
    "timbre_detective_game": "timbre_detective_core",
    "timbre_match_game": "timbre_detective_core",
    "timbre_evidence_match": "timbre_detective_core",
    "form_treasure_game": "form_treasure_core",
    "form_map_game": "form_treasure_core",
}

PRODUCTION_TEMPLATE_TEXT_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "composition_puzzle_core",
        (
            "拼图创编工坊",
            "拼图创编",
            "拼图创作",
            "节奏拼图",
            "节奏创编",
            "时值拼图",
            "旋律拼图",
            "旋律创作",
            "旋律创编",
            "旋律创造",
            "音级创编",
            "五声音阶创编",
            "旋律节奏拼图",
            "音符拼图",
            "旋律和节奏",
            "节奏卡",
            "拖拽拼成",
            "素材拼成",
        ),
    ),
    (
        "form_treasure_core",
        ("曲式寻宝", "曲式", "ABA", "回旋", "重复对比", "段落结构", "主题再现", "音乐结构"),
    ),
    (
        "timbre_detective_core",
        ("音色侦探", "音色", "乐器听辨", "乐器辨别", "声音证据", "声音线索", "笛子", "二胡", "小提琴"),
    ),
    (
        "solfege_target_core",
        ("唱名打靶", "唱名靶", "听音击中", "击中唱名", "模唱确认", "唱名听辨"),
    ),
    (
        "beat_guardian_core",
        ("节拍守卫", "强拍", "弱拍", "拍号", "稳拍", "进入时机", "二拍子", "三拍子", "四拍子"),
    ),
    (
        "rhythm_echo_core",
        ("节奏复刻", "节奏接龙", "听后拍回", "跟拍", "节奏模仿", "复刻节奏"),
    ),
    (
        "pitch_ladder_core",
        ("音高探路者", "音高阶梯", "音高爬梯", "音高台阶", "音高高低", "旋律走向", "上行下行", "级进跳进"),
    ),
)


DOCUMENT_GAME_ACTIVITY_MAP: dict[str, dict[str, Any]] = {
    "听音识曲": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["听辨", "选择", "说出依据"],
        "implementation_note": "适合作为导入或欣赏听辨，不单独作为主模板，需加入音乐依据反馈。",
        "selected_for_agent": False,
    },
    "曲风匹配": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["比较", "匹配", "描述风格特征"],
        "implementation_note": "可并入音色/风格证据匹配类模板。",
        "selected_for_agent": True,
        "template_id": "timbre_evidence_match",
    },
    "音符彩蛋": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["探索"],
        "implementation_note": "趣味强但学习证据弱，暂不写入主模板。",
        "selected_for_agent": False,
    },
    "节奏点按": {
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "learning_depth": ["听辨", "复现", "节拍稳定"],
        "implementation_note": "可作为节拍闯关的操作模式。",
        "selected_for_agent": True,
        "template_id": "rhythm_echo_chain",
    },
    "节奏拼图": {
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["听辨", "重建", "播放验证", "修正", "迁移创编"],
        "implementation_note": "优先写入，适合节奏、时值、附点、切分、休止。",
        "selected_for_agent": True,
        "template_id": "rhythm_rebuild_challenge",
    },
    "节拍闯关": {
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "learning_depth": ["示范", "复刻", "即时评分", "再次表现"],
        "implementation_note": "优先写入，适合表现性活动。",
        "selected_for_agent": True,
        "template_id": "rhythm_echo_chain",
    },
    "节奏接龙": {
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["聆听记忆", "复现", "延续", "合作表达"],
        "implementation_note": "适合小组接力和节奏表现。",
        "selected_for_agent": True,
        "template_id": "rhythm_echo_chain",
    },
    "高低选位": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "learning_depth": ["听辨", "定位", "模唱"],
        "implementation_note": "并入音高台阶，必须使用具体唱名或音级。",
        "selected_for_agent": True,
        "template_id": "pitch_ladder_game",
    },
    "音阶游戏": {
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["听辨", "定位", "模唱", "短句迁移"],
        "implementation_note": "优先写入，可服务 sol-mi、do-re-mi、五声音阶。",
        "selected_for_agent": True,
        "template_id": "pitch_ladder_game",
    },
    "音高定位": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "learning_depth": ["听辨", "定位", "播放验证"],
        "implementation_note": "优先写入，避免抽象上行下行替代具体音。",
        "selected_for_agent": True,
        "template_id": "pitch_ladder_game",
    },
    "音符配对": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "learning_depth": ["识别", "匹配", "播放验证", "说出规则"],
        "implementation_note": "写入为乐理证据配对，不做纯图片配对。",
        "selected_for_agent": True,
        "template_id": "notation_match_lab",
    },
    "谱线寻踪": {
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "learning_depth": ["读谱", "定位", "唱奏验证"],
        "implementation_note": "可实现五线谱点击，但需要简化到固定音域。",
        "selected_for_agent": True,
        "template_id": "staff_position_finder",
    },
    "符号速认": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "performance",
        "learning_depth": ["识别", "反应", "应用到读谱"],
        "implementation_note": "不单独做模板，并入音符配对或谱线寻踪。",
        "selected_for_agent": False,
        "template_id": "notation_match_lab",
    },
    "时值测试": {
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["分类", "比较", "播放验证", "复现"],
        "implementation_note": "并入节奏重建挑战。",
        "selected_for_agent": True,
        "template_id": "rhythm_rebuild_challenge",
    },
    "乐句拼图": {
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["结构感知", "排序", "演唱验证"],
        "implementation_note": "适合学唱和结构理解。",
        "selected_for_agent": True,
        "template_id": "phrase_rebuild_singing",
    },
    "跟唱闯关": {
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "learning_depth": ["听范唱", "跟唱", "分句打卡", "优化表现"],
        "implementation_note": "可先做范唱同步和自评，不做实时声音识别。",
        "selected_for_agent": True,
        "template_id": "phrase_rebuild_singing",
    },
    "空句补乐": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "learning_depth": ["听前后文", "选择", "演唱验证"],
        "implementation_note": "并入乐句重建类。",
        "selected_for_agent": True,
        "template_id": "phrase_rebuild_singing",
    },
    "闻声辨器": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["听辨", "匹配", "说明音色依据"],
        "implementation_note": "优先写入，适合音色听辨。",
        "selected_for_agent": True,
        "template_id": "timbre_evidence_match",
    },
    "音色连连": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["比较", "连线", "说明音色证据"],
        "implementation_note": "并入音色证据匹配。",
        "selected_for_agent": True,
        "template_id": "timbre_evidence_match",
    },
    "乐器拼装": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["认识乐器", "试听音色"],
        "implementation_note": "素材依赖高，暂不作为核心模板。",
        "selected_for_agent": False,
    },
    "乐章联想": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["欣赏", "联想", "说明音乐证据"],
        "implementation_note": "可并入表现决策/情绪控制，不做纯选图。",
        "selected_for_agent": True,
        "template_id": "expression_decision_game",
    },
    "片段拼接": {
        "activity_fit": ["listening", "creation"],
        "preferred_activity": "listening",
        "learning_depth": ["结构聆听", "排序", "播放验证", "说明曲式依据"],
        "implementation_note": "优先写入，适合曲式、段落、乐句结构。",
        "selected_for_agent": True,
        "template_id": "segment_ordering_studio",
    },
    "流派分辨": {
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "learning_depth": ["听辨", "分类", "说明风格依据"],
        "implementation_note": "并入音色/风格证据匹配。",
        "selected_for_agent": True,
        "template_id": "timbre_evidence_match",
    },
    "随心编曲": {
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "learning_depth": ["选择材料", "约束创编", "试听修正", "展示说明"],
        "implementation_note": "必须改成约束创编，不能完全随心乱拼。",
        "selected_for_agent": True,
        "template_id": "constrained_composition_lab",
    },
    "填词拼句": {
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "learning_depth": ["语言节奏", "匹配旋律", "演唱验证"],
        "implementation_note": "二期模板，需歌词和旋律框架。",
        "selected_for_agent": False,
    },
    "乐段重组": {
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "learning_depth": ["结构设计", "组合", "试听修正", "说明编排理由"],
        "implementation_note": "优先写入，可服务创编和曲式理解。",
        "selected_for_agent": True,
        "template_id": "segment_ordering_studio",
    },
    "音乐测试": {
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "learning_depth": ["综合巩固"],
        "implementation_note": "作为总结组件，不作为主游戏模板。",
        "selected_for_agent": False,
    },
    "通关集星": {
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "learning_depth": ["激励", "进度反馈"],
        "implementation_note": "作为奖励系统，不作为独立游戏模板。",
        "selected_for_agent": False,
    },
}


GAME_FORM_LIBRARY: dict[str, dict[str, Any]] = {
    "rhythm_race_game": {
        "label": "节奏时值赛跑",
        "family": "rhythm",
        "primary": "rhythm_race_game",
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "source_game_forms": ["节奏拼图", "节拍闯关", "节奏接龙", "时值测试"],
        "learning_depth": ["听辨", "复现", "播放验证", "修正", "迁移表现"],
        "keywords": ["节奏", "时值", "音符", "拍", "附点", "切分", "休止", "强弱"],
        "components": ["countdown_start", "drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress"],
        "default_concept": "节奏时值",
        "mechanic": "把不同节奏单位变成行动速度不同的角色，学生拖拽排序后点击开始，角色按时值或拍点完成挑战。",
        "student_actions": ["观察角色对应的节奏规则", "拖拽角色组成节奏句", "点击开始挑战并跟随拍击", "根据反馈调整后再挑战"],
        "loop": ["读规则卡", "排出节奏顺序", "播放并观察动作", "拍击或说出音乐理由", "通关或重试"],
        "failure_state": "顺序为空、拍点关系不完整或学生无法说明判断依据时，引导重新听、重新排。",
        "progression": ["先做 1 小节", "再做 2 小节", "最后加入课堂拍击或律动表现"],
    },
    "rhythm_rebuild_challenge": {
        "label": "节奏重建挑战",
        "family": "rhythm",
        "primary": "rhythm_race_game",
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "source_game_forms": ["节奏拼图", "时值测试"],
        "learning_depth": ["听目标", "重建节奏", "播放对比", "修改", "拍击迁移"],
        "keywords": ["节奏拼图", "节奏重建", "时值测试", "全音符", "二分音符", "四分音符", "附点", "切分", "休止"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "节奏时值",
        "mechanic": "学生先试听目标节奏，再用标准节奏材料重建节奏句，播放自己的排列进行对比，最后拍击或创编迁移。",
        "student_actions": ["试听目标节奏", "拖拽节奏材料重建", "播放对比并修正", "拍击或创编一个新节奏句"],
        "loop": ["听目标", "重建", "试听自己", "检查反馈", "拍击或创编迁移"],
        "failure_state": "材料顺序、时值或小节长度不符合目标时，保留学生答案并提示重听对应位置。",
        "progression": ["先重建 2 个材料", "再重建完整小节", "最后迁移创编新节奏"],
    },
    "rhythm_echo_chain": {
        "label": "节奏复刻接龙",
        "family": "rhythm",
        "primary": "rhythm_race_game",
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "source_game_forms": ["节奏点按", "节拍闯关", "节奏接龙"],
        "learning_depth": ["听示范", "复刻", "即时评分", "接龙延续", "稳定表现"],
        "keywords": ["节奏点按", "节拍闯关", "节奏接龙", "复刻", "跟拍", "接龙"],
        "components": ["countdown_start", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "节奏与拍点",
        "mechanic": "系统播放示范节奏，学生用点击、拖拽或拍点卡复刻；通过后续接一个短节奏，形成表现性接龙。",
        "student_actions": ["听示范节奏", "复刻拍点", "查看稳定度反馈", "接出下一小节并拍击展示"],
        "loop": ["听示范", "复刻", "检查", "接龙", "表现展示"],
        "failure_state": "拍点不稳或接龙脱离目标节奏时，回放原示范并降低速度重试。",
        "progression": ["先复刻 2 拍", "再复刻 1 小节", "最后完成接龙表现"],
    },
    "melody_path_game": {
        "label": "旋律爬坡路线",
        "family": "melody",
        "primary": "melody_path_game",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "source_game_forms": ["高低选位", "音高定位"],
        "learning_depth": ["听辨", "定位", "播放验证", "模唱"],
        "keywords": ["旋律", "音高", "上行", "下行", "级进", "跳进", "旋律线", "模唱"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "旋律走向",
        "mechanic": "把旋律高低变化变成路线节点，学生选择上行、下行、保持或跳进动作，播放后验证路线是否贴合听感。",
        "student_actions": ["听辨旋律变化", "选择或拖拽路线动作", "播放验证高低走向", "模唱并说明路线依据"],
        "loop": ["听或看旋律提示", "选择路线动作", "播放验证", "模唱确认", "进入更长乐句"],
        "failure_state": "路线方向与旋律听感不符，或只完成视觉连线但无法模唱时，需要回到听辨再试。",
        "progression": ["先判断上行/下行", "再加入保持音", "最后区分级进和跳进"],
    },
    "sol_mi_pitch_game": {
        "label": "sol-mi 音高台阶",
        "family": "melody",
        "primary": "sol_mi_pitch_game",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "performance",
        "source_game_forms": ["音阶游戏", "音高定位", "高低选位"],
        "learning_depth": ["听辨唱名", "定位音高", "播放验证", "模唱迁移"],
        "keywords": ["sol", "mi", "唱名", "高低音", "音高关系", "音列", "模唱"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "sol-mi 音高关系",
        "mechanic": "把 sol 和 mi 做成两张具体唱名卡，学生先听目标音列，再拖拽唱名卡还原顺序，播放后立即模唱验证。",
        "student_actions": ["试听目标音列", "拖拽 sol/mi 唱名卡", "检查闯关结果", "模唱并说出高低关系"],
        "loop": ["听音列", "摆唱名卡", "试听自己的排列", "检查闯关", "模唱回应"],
        "failure_state": "如果唱名顺序与听到的音列不一致，或学生摆对却唱不出来，需要重听后重新摆放并模唱。",
        "progression": ["先还原 2 个音", "再还原 3 到 4 个音", "最后边摆边模唱完整音列"],
    },
    "pitch_ladder_game": {
        "label": "音高台阶定位",
        "family": "melody",
        "primary": "sol_mi_pitch_game",
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "source_game_forms": ["高低选位", "音阶游戏", "音高定位"],
        "learning_depth": ["听辨", "定位", "试听验证", "模唱", "短句迁移"],
        "keywords": ["高低选位", "音阶游戏", "音高定位", "do", "re", "mi", "sol", "唱名", "音阶"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "音高与唱名",
        "mechanic": "把具体唱名或音级放在音高台阶上，学生听目标音列后定位，再播放自己的排列并模唱。",
        "student_actions": ["试听目标音列", "把唱名卡放到台阶", "试听自己的音列", "模唱并说明高低关系"],
        "loop": ["听音列", "定位", "试听", "检查", "模唱迁移"],
        "failure_state": "位置和实际音高不一致时，提示重听具体唱名，不能用抽象方向代替。",
        "progression": ["先定位两个音", "再定位三到四个音", "最后模唱或创编短句"],
    },
    "timbre_detective_game": {
        "label": "音色侦探",
        "family": "listening",
        "primary": "timbre_detective_game",
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "source_game_forms": ["闻声辨器", "音色连连", "曲风匹配", "流派分辨"],
        "learning_depth": ["听辨", "匹配", "比较", "说明音色或风格依据"],
        "keywords": ["音色", "乐器", "听辨", "管弦", "民族乐器", "钢琴", "小提琴", "长笛", "古筝", "琵琶", "二胡"],
        "components": ["drag_drop_puzzle", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "乐器音色",
        "mechanic": "把声音特征、乐器名称和音乐形象做成证据卡，学生先听再匹配，提交后必须说出听辨依据。",
        "student_actions": ["先聆听音色线索", "拖拽证据卡完成匹配", "查看提示并修正", "说出音色判断依据"],
        "loop": ["听线索", "匹配证据", "检查反馈", "补充理由", "解锁下一条线索"],
        "failure_state": "只凭图像猜测或无法说明音色特征时，提示重新聆听发声特点。",
        "progression": ["先辨认单个乐器", "再匹配音乐形象", "最后比较相近音色"],
    },
    "timbre_evidence_match": {
        "label": "音色证据匹配",
        "family": "listening",
        "primary": "timbre_detective_game",
        "activity_fit": ["listening"],
        "preferred_activity": "listening",
        "source_game_forms": ["闻声辨器", "音色连连", "曲风匹配", "流派分辨"],
        "learning_depth": ["先听", "找证据", "匹配", "比较", "说依据"],
        "keywords": ["闻声辨器", "音色连连", "曲风匹配", "流派分辨", "音色证据", "风格匹配"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "音色与风格听辨",
        "mechanic": "学生先听声音线索，再把乐器、音色特征或风格证据拖到对应位置，提交后必须说明听辨依据。",
        "student_actions": ["聆听声音线索", "拖拽证据卡匹配", "重新听并修正", "说出音色或风格依据"],
        "loop": ["听线索", "找证据", "匹配", "反馈", "说明依据"],
        "failure_state": "只看图片猜测或不能说出声音特征时，必须回到重听。",
        "progression": ["先辨单个音色", "再比较相近音色", "最后判断风格或流派"],
    },
    "notation_match_lab": {
        "label": "乐理证据配对",
        "family": "theory",
        "primary": "music_match_game",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "source_game_forms": ["音符配对", "符号速认", "时值测试"],
        "learning_depth": ["识别符号", "匹配名称", "播放验证", "应用到读谱"],
        "keywords": ["音符配对", "符号速认", "乐理", "休止符", "升降号", "五线谱音符", "名称匹配"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "乐理符号认知",
        "mechanic": "把符号、名称、声音或时值做成证据卡，学生配对后播放验证并说出规则。",
        "student_actions": ["观察符号", "匹配名称或声音", "播放验证", "说出乐理规则"],
        "loop": ["看符号", "配对", "试听", "检查", "应用到读谱"],
        "failure_state": "只记住图形但不能连接声音或读谱用途时，需要回到播放验证。",
        "progression": ["先符号和名称配对", "再加入声音或时值", "最后放入小谱例"],
    },
    "staff_position_finder": {
        "label": "谱线寻踪",
        "family": "theory",
        "primary": "music_match_game",
        "activity_fit": ["performance"],
        "preferred_activity": "performance",
        "source_game_forms": ["谱线寻踪"],
        "learning_depth": ["读谱", "点击定位", "唱奏验证"],
        "keywords": ["谱线寻踪", "五线谱", "谱线", "间", "音位", "读谱"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "五线谱音位",
        "mechanic": "学生在简化五线谱上点击或拖拽目标音位，播放该音并用唱名或乐器验证。",
        "student_actions": ["观察目标音名", "点击谱线位置", "播放验证", "唱出或奏出该音"],
        "loop": ["读提示", "定位", "试听", "检查", "唱奏迁移"],
        "failure_state": "音位和播放音高不一致时，提示回到线/间关系。",
        "progression": ["先固定少量音", "再扩大音域", "最后放入短句读谱"],
    },
    "pentatonic_grid_game": {
        "label": "五声宫格拼图",
        "family": "creation",
        "primary": "pentatonic_grid_game",
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "source_game_forms": ["随心编曲", "乐段重组"],
        "learning_depth": ["选择音级", "约束创编", "试听修正", "说明风格依据"],
        "keywords": ["五声", "宫", "商", "角", "徵", "羽", "调式", "民族", "创编", "拼图"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "五声音阶与民族调式",
        "mechanic": "把宫、商、角、徵、羽做成音级卡，学生拼出短句并试听，最后说明为什么有相应风格。",
        "student_actions": ["选择五声音级", "拖拽拼出短乐句", "播放试听风格", "分享调式或风格依据"],
        "loop": ["领任务", "选音级", "拼短句", "试听修正", "展示说明"],
        "failure_state": "使用了不符合任务的音级，或短句无法形成开始、发展、收束时，需要调整。",
        "progression": ["先拼 2 小节", "再加入节奏变化", "最后做小组展示"],
    },
    "constrained_composition_lab": {
        "label": "约束创编工坊",
        "family": "creation",
        "primary": "pentatonic_grid_game",
        "activity_fit": ["creation"],
        "preferred_activity": "creation",
        "source_game_forms": ["随心编曲", "乐段重组"],
        "learning_depth": ["调用所学要素", "约束创编", "试听修正", "展示说明"],
        "keywords": ["随心编曲", "创编", "编曲", "旋律方块", "乐段重组", "自由组合", "小曲"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "音乐素材创编",
        "mechanic": "学生只能使用本课学过的节奏、音高或调式材料进行创编，试听后修改，并说明用了哪个音乐要素。",
        "student_actions": ["选择本课材料", "拼成短句或乐段", "试听并修改", "展示并说明创编依据"],
        "loop": ["选材料", "拼接", "试听", "修改", "展示说明"],
        "failure_state": "作品脱离本课音乐要素或无法播放成句时，提示回到材料限制重新组织。",
        "progression": ["先完成 1 小节", "再形成问答句", "最后小组展示"],
    },
    "segment_ordering_studio": {
        "label": "乐段结构重建",
        "family": "structure",
        "primary": "music_match_game",
        "activity_fit": ["listening", "creation"],
        "preferred_activity": "listening",
        "source_game_forms": ["片段拼接", "乐段重组", "乐句拼图"],
        "learning_depth": ["结构聆听", "排序", "播放验证", "说明曲式依据", "重组创作"],
        "keywords": ["片段拼接", "乐段重组", "乐句拼图", "乐句", "乐段", "曲式", "顺序", "结构"],
        "components": ["drag_drop_puzzle", "playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "乐句与曲式结构",
        "mechanic": "学生聆听多个片段，按乐句或乐段关系排序，播放验证结构是否完整，再说明依据或进行重组创作。",
        "student_actions": ["试听片段", "拖拽排序", "播放完整结构", "说明乐句或曲式依据"],
        "loop": ["听片段", "排序", "整段播放", "检查反馈", "说明或重组"],
        "failure_state": "顺序破坏起承转合或重复/对比关系时，提示重听片段开头和收束。",
        "progression": ["先排两个乐句", "再排完整段落", "最后尝试重组表达"],
    },
    "phrase_rebuild_singing": {
        "label": "乐句学唱重建",
        "family": "singing",
        "primary": "melody_path_game",
        "activity_fit": ["performance", "creation"],
        "preferred_activity": "performance",
        "source_game_forms": ["乐句拼图", "跟唱闯关", "空句补乐"],
        "learning_depth": ["听范唱", "乐句排序", "跟唱验证", "表现优化"],
        "keywords": ["乐句拼图", "跟唱闯关", "空句补乐", "学唱", "范唱", "歌词", "乐句"],
        "components": ["playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "乐句演唱与结构",
        "mechanic": "学生先听范唱或前后文，再重建缺失乐句，播放验证后进行跟唱和表现优化。",
        "student_actions": ["听范唱或前后文", "拖拽乐句排序或补空", "播放验证", "跟唱并优化表现"],
        "loop": ["听", "重建", "验证", "跟唱", "优化"],
        "failure_state": "乐句顺序不通或不能唱出连贯乐句时，回到范唱重听。",
        "progression": ["先补一个乐句", "再排完整乐段", "最后跟唱展示"],
    },
    "group_relay_game": {
        "label": "小组接力挑战",
        "family": "collaboration",
        "primary": "group_relay_game",
        "keywords": ["小组", "合作", "接力", "展示", "表演", "轮流", "评价"],
        "components": ["level_map", "countdown_start", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "合作表现",
        "mechanic": "把课堂任务拆成小组轮次，每组负责一个节奏、乐句、声部或表现动作，接力完成后进入展示评价。",
        "student_actions": ["领取小组轮次任务", "完成本组音乐操作", "交给下一组继续", "全班展示并互评"],
        "loop": ["分配轮次", "小组完成任务", "接力到下一组", "合并展示", "教师总结评价"],
        "failure_state": "轮次中断、任务目标不清或小组无法接上前一组结果时，回到上一轮提示再试。",
        "progression": ["先单组完成", "再两组接力", "最后全班合并展示"],
    },
    "expression_control_game": {
        "label": "音乐表情控制台",
        "family": "expression",
        "primary": "expression_control_game",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "source_game_forms": ["乐章联想"],
        "learning_depth": ["聆听", "表现决策", "对比验证", "说明依据"],
        "keywords": ["力度", "速度", "强弱", "渐强", "渐弱", "快慢", "情绪", "形象"],
        "components": ["playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "音乐表现变化",
        "mechanic": "把力度、速度、情绪或音乐形象变成控制卡，学生选择后观察反馈，并说明为什么符合音乐听感。",
        "student_actions": ["聆听或观察音乐形象", "选择表现控制项", "播放验证变化", "说明判断依据"],
        "loop": ["聆听提示", "调节控制项", "观察反馈", "说明理由", "比较另一种选择"],
        "failure_state": "选择与音乐形象不匹配，或不能说明力度、速度与情绪关系时，引导对比再试。",
        "progression": ["先单项判断", "再判断变化过程", "最后连接歌曲情绪或人物形象"],
    },
    "expression_decision_game": {
        "label": "音乐形象决策",
        "family": "expression",
        "primary": "expression_control_game",
        "activity_fit": ["listening", "performance"],
        "preferred_activity": "listening",
        "source_game_forms": ["乐章联想"],
        "learning_depth": ["聆听", "选择情绪场景", "对比声音证据", "说明依据"],
        "keywords": ["乐章联想", "情绪", "场景", "插画", "形象", "意境"],
        "components": ["playback_controls", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "音乐情绪与形象",
        "mechanic": "学生先聆听音乐，再选择情绪或场景，但必须用力度、速度、音色、旋律等声音证据说明理由。",
        "student_actions": ["聆听片段", "选择情绪或场景", "对比音乐证据", "说明判断依据"],
        "loop": ["听", "选", "对比", "反馈", "说依据"],
        "failure_state": "只凭画面联想而没有音乐证据时，引导回到声音线索。",
        "progression": ["先选情绪", "再找音乐证据", "最后用动作或语言表现"],
    },
    "lesson_mission_game": {
        "label": "课例任务闯关",
        "family": "mission",
        "primary": "lesson_mission_game",
        "activity_fit": ["listening", "performance", "creation"],
        "preferred_activity": "performance",
        "source_game_forms": ["综合课例任务"],
        "learning_depth": ["目标理解", "操作", "反馈", "表达", "迁移"],
        "keywords": [],
        "components": ["level_map", "drag_drop_puzzle", "timing_feedback", "badge_progress", "reflection_panel"],
        "default_concept": "综合音乐感知",
        "mechanic": "把教案核心目标拆成短任务，学生通过选择、排序、匹配或展示完成学习闭环。",
        "student_actions": ["理解课堂任务", "完成页面操作挑战", "查看即时反馈", "分享音乐理由"],
        "loop": ["进入任务", "完成操作", "查看反馈", "修正再试", "课堂分享"],
        "failure_state": "操作脱离音乐目标或没有说明理由时，引导学生回到本课音乐要素。",
        "progression": ["先完成基础挑战", "再加入同伴互评", "最后回到课堂展示"],
    },
}


GAME_TYPE_ALIASES = {
    "rhythm_animal_race": "rhythm_race_game",
    "note_value_race": "rhythm_race_game",
    "meter_orbit_game": "rhythm_race_game",
    "meter_gate_game": "rhythm_race_game",
    "dotted_rhythm_bounce": "rhythm_race_game",
    "syncopation_flag_game": "rhythm_race_game",
    "rest_light_game": "rhythm_race_game",
    "rhythm_rebuild_challenge": "rhythm_rebuild_challenge",
    "rhythm_echo_chain": "rhythm_echo_chain",
    "pitch_flying_game": "melody_path_game",
    "pitch_path_game": "melody_path_game",
    "melody_path_game": "melody_path_game",
    "pitch_ladder_game": "pitch_ladder_game",
    "solmi_pitch_ladder": "sol_mi_pitch_game",
    "sol_mi_pitch_game": "sol_mi_pitch_game",
    "interval_step_game": "melody_path_game",
    "phrase_pair_game": "melody_path_game",
    "music_match_game": "timbre_detective_game",
    "timbre_match_game": "timbre_detective_game",
    "timbre_detective_game": "timbre_detective_game",
    "timbre_evidence_match": "timbre_evidence_match",
    "notation_match_lab": "notation_match_lab",
    "staff_position_finder": "staff_position_finder",
    "mode_puzzle_game": "pentatonic_grid_game",
    "creation_mission_game": "pentatonic_grid_game",
    "constrained_composition_lab": "constrained_composition_lab",
    "segment_ordering_studio": "segment_ordering_studio",
    "phrase_rebuild_singing": "phrase_rebuild_singing",
    "expression_decision_game": "expression_decision_game",
    "custom_music_game": "lesson_mission_game",
}


def canonical_game_type(game_type: str) -> str:
    raw = str(game_type or "").strip()
    if raw in GAME_FORM_LIBRARY:
        return raw
    return GAME_TYPE_ALIASES.get(raw, raw if raw in GAME_FORM_LIBRARY else "lesson_mission_game")


def game_form_for_type(game_type: str) -> dict[str, Any]:
    canonical = canonical_game_type(game_type)
    return GAME_FORM_LIBRARY[canonical]


def infer_game_type_from_text(text: str) -> str:
    source = str(text or "")
    best_type = "lesson_mission_game"
    best_score = 0
    for game_name, mapping in DOCUMENT_GAME_ACTIVITY_MAP.items():
        if game_name in source and mapping.get("selected_for_agent") and mapping.get("template_id"):
            best_type = str(mapping["template_id"])
            best_score = max(best_score, 100)
    for game_type, form in GAME_FORM_LIBRARY.items():
        score = sum(source.count(keyword) for keyword in form.get("keywords", []) if keyword)
        if any(name in source for name in form.get("source_game_forms", [])):
            score += 3
        if score > best_score:
            best_type = game_type
            best_score = score
    return best_type


def detect_template_match_from_text(text: str) -> str:
    """Return a matched template only for explicit, high-confidence template hits."""

    source = str(text or "")
    lowered = source.lower()
    for template_id in PRODUCTION_TEMPLATE_IDS:
        if template_id in source:
            return template_id
    for template_id, keywords in PRODUCTION_TEMPLATE_TEXT_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return template_id
    for game_name, mapping in DOCUMENT_GAME_ACTIVITY_MAP.items():
        if game_name in source and mapping.get("selected_for_agent") and mapping.get("template_id"):
            template_id = str(mapping["template_id"])
            return LEGACY_TO_PRODUCTION_TEMPLATE_IDS.get(template_id, template_id)
    return ""


def document_game_activity_map() -> dict[str, dict[str, Any]]:
    return DOCUMENT_GAME_ACTIVITY_MAP


def selected_learning_game_templates() -> dict[str, dict[str, Any]]:
    return {
        game_type: form
        for game_type, form in GAME_FORM_LIBRARY.items()
        if form.get("source_game_forms") and game_type != "lesson_mission_game"
    }


def build_music_game_blueprint(
    *,
    game_type: str,
    concept: str,
    goal: str,
    stage: str = "",
    source_name: str = "",
) -> dict[str, Any]:
    canonical = canonical_game_type(game_type)
    form = GAME_FORM_LIBRARY[canonical]
    display_concept = concept or form["default_concept"]
    display_goal = goal or f"让学生通过游戏操作理解“{display_concept}”，并能说出判断依据。"
    return {
        "game_type": canonical,
        "game_family": form["family"],
        "activity_fit": list(form.get("activity_fit", [])),
        "preferred_activity": form.get("preferred_activity", ""),
        "source_game_forms": list(form.get("source_game_forms", [])),
        "learning_depth": list(form.get("learning_depth", [])),
        "game_name": source_name or form["label"],
        "music_concept": display_concept,
        "goal": display_goal,
        "mechanic": form["mechanic"],
        "primary_interaction": form["primary"],
        "components": list(form["components"]),
        "student_actions": list(form["student_actions"]),
        "core_loop": list(form["loop"]),
        "failure_state": form["failure_state"],
        "progression": list(form["progression"]),
        "target_session_minutes": "3-5",
        "stage": stage,
    }
