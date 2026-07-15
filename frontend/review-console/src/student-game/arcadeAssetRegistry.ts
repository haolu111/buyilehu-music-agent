import type { StudentGameState } from "./types";

export type ArcadeTemplateAssetKey =
  | "beat_guardian_core"
  | "rhythm_echo_core"
  | "pitch_ladder_core"
  | "solfege_target_core"
  | "timbre_detective_core"
  | "form_treasure_core";

export type ArcadeAssetState = "idle" | "hit" | "miss" | "win";

export type ArcadeAssetStateSpec = {
  label: string;
  glyph: string;
  cssClass: string;
};

export type ArcadeTemplateAssets = {
  templateId: ArcadeTemplateAssetKey | "default";
  paletteClass: string;
  heroName: string;
  heroRole: string;
  heroGlyph: string;
  stageTitle: string;
  stageProp: string;
  rewardName: string;
  rewardGlyph: string;
  startCta: string;
  successFx: string;
  failFx: string;
  referenceGame: {
    title: string;
    pattern: string;
  };
  states: Record<ArcadeAssetState, ArcadeAssetStateSpec>;
};

const DEFAULT_ASSETS: ArcadeTemplateAssets = {
  templateId: "default",
  paletteClass: "arcade-palette-music",
  heroName: "小乐手",
  heroRole: "音乐挑战者",
  heroGlyph: "乐",
  stageTitle: "音乐闯关",
  stageProp: "旋律舞台",
  rewardName: "通关章",
  rewardGlyph: "章",
  startCta: "开始挑战",
  successFx: "奖励闪光",
  failFx: "回弹提示",
  referenceGame: {
    title: "4399 闯关小游戏",
    pattern: "短回合、强反馈、星级奖励"
  },
  states: {
    idle: { label: "待命", glyph: "乐", cssClass: "sprite-idle" },
    hit: { label: "命中", glyph: "准", cssClass: "sprite-hit" },
    miss: { label: "受挫", glyph: "再", cssClass: "sprite-miss" },
    win: { label: "胜利", glyph: "胜", cssClass: "sprite-win" }
  }
};

const ASSETS: Record<ArcadeTemplateAssetKey, ArcadeTemplateAssets> = {
  beat_guardian_core: {
    templateId: "beat_guardian_core",
    paletteClass: "arcade-palette-guardian",
    heroName: "护盾守卫",
    heroRole: "强拍充能员",
    heroGlyph: "盾",
    stageTitle: "充能护盾",
    stageProp: "弱拍怪物",
    rewardName: "护盾徽章",
    rewardGlyph: "盾",
    startCta: "开始充能",
    successFx: "护盾震波",
    failFx: "护盾裂缝",
    referenceGame: {
      title: "节拍护盾",
      pattern: "看呼吸周期预判第 1 拍，弱拍蓄势"
    },
    states: {
      idle: { label: "观察呼吸", glyph: "盾", cssClass: "sprite-idle" },
      hit: { label: "同步充能", glyph: "充", cssClass: "sprite-hit" },
      miss: { label: "护盾裂缝", glyph: "裂", cssClass: "sprite-miss" },
      win: { label: "震波稳定", glyph: "稳", cssClass: "sprite-win" }
    }
  },
  rhythm_echo_core: {
    templateId: "rhythm_echo_core",
    paletteClass: "arcade-palette-echo",
    heroName: "节奏飞船",
    heroRole: "轨道记忆员",
    heroGlyph: "拍",
    stageTitle: "节奏轨道",
    stageProp: "飞行音符链",
    rewardName: "节奏星",
    rewardGlyph: "星",
    startCta: "听示范",
    successFx: "光链点亮",
    failFx: "断链回弹",
    referenceGame: {
      title: "节奏大师",
      pattern: "轨道拍点、连击、漏拍断链"
    },
    states: {
      idle: { label: "轨道待命", glyph: "轨", cssClass: "sprite-idle" },
      hit: { label: "音符连线", glyph: "连", cssClass: "sprite-hit" },
      miss: { label: "光链断开", glyph: "断", cssClass: "sprite-miss" },
      win: { label: "节奏星点亮", glyph: "亮", cssClass: "sprite-win" }
    }
  },
  pitch_ladder_core: {
    templateId: "pitch_ladder_core",
    paletteClass: "arcade-palette-ladder",
    heroName: "登山小队",
    heroRole: "音高路线员",
    heroGlyph: "高",
    stageTitle: "音高山路",
    stageProp: "云梯平台",
    rewardName: "旋律宝石",
    rewardGlyph: "石",
    startCta: "听音出发",
    successFx: "登顶插旗",
    failFx: "滑落回弹",
    referenceGame: {
      title: "音乐熊过关",
      pattern: "平台闯关、跳跃路线、失误回退"
    },
    states: {
      idle: { label: "山脚待命", glyph: "梯", cssClass: "sprite-idle" },
      hit: { label: "跳上平台", glyph: "跳", cssClass: "sprite-hit" },
      miss: { label: "路线滑落", glyph: "滑", cssClass: "sprite-miss" },
      win: { label: "登顶插旗", glyph: "旗", cssClass: "sprite-win" }
    }
  },
  solfege_target_core: {
    templateId: "solfege_target_core",
    paletteClass: "arcade-palette-target",
    heroName: "靶场队长",
    heroRole: "音名射手",
    heroGlyph: "唱",
    stageTitle: "音名靶场",
    stageProp: "唱回星门",
    rewardName: "靶心星",
    rewardGlyph: "靶",
    startCta: "听目标音",
    successFx: "星门打开",
    failFx: "准星偏移",
    referenceGame: {
      title: "泡泡龙",
      pattern: "点击目标、命中爆点、错靶回弹"
    },
    states: {
      idle: { label: "瞄准待命", glyph: "准", cssClass: "sprite-idle" },
      hit: { label: "击中音名", glyph: "中", cssClass: "sprite-hit" },
      miss: { label: "准星偏移", glyph: "偏", cssClass: "sprite-miss" },
      win: { label: "唱回开门", glyph: "门", cssClass: "sprite-win" }
    }
  },
  timbre_detective_core: {
    templateId: "timbre_detective_core",
    paletteClass: "arcade-palette-detective",
    heroName: "声音侦探",
    heroRole: "证据推理员",
    heroGlyph: "侦",
    stageTitle: "声音案桌",
    stageProp: "声纹证物",
    rewardName: "破案印章",
    rewardGlyph: "印",
    startCta: "听证物",
    successFx: "盖章破案",
    failFx: "线索回弹",
    referenceGame: {
      title: "侦探找茬",
      pattern: "观察证据、锁定目标、提交推理"
    },
    states: {
      idle: { label: "查看案卷", glyph: "案", cssClass: "sprite-idle" },
      hit: { label: "钉上红线", glyph: "证", cssClass: "sprite-hit" },
      miss: { label: "线索不足", glyph: "查", cssClass: "sprite-miss" },
      win: { label: "盖章破案", glyph: "破", cssClass: "sprite-win" }
    }
  },
  form_treasure_core: {
    templateId: "form_treasure_core",
    paletteClass: "arcade-palette-treasure",
    heroName: "曲式寻宝队",
    heroRole: "结构探险员",
    heroGlyph: "图",
    stageTitle: "藏宝图路线",
    stageProp: "结构地图碎片",
    rewardName: "结构宝箱",
    rewardGlyph: "箱",
    startCta: "听第一段",
    successFx: "宝箱开启",
    failFx: "路线摇晃",
    referenceGame: {
      title: "藏宝路线",
      pattern: "听段落、放卡连桥、开宝箱"
    },
    states: {
      idle: { label: "展开地图", glyph: "图", cssClass: "sprite-idle" },
      hit: { label: "路线发光", glyph: "路", cssClass: "sprite-hit" },
      miss: { label: "路线摇晃", glyph: "摇", cssClass: "sprite-miss" },
      win: { label: "宝箱开启", glyph: "宝", cssClass: "sprite-win" }
    }
  }
};

export function arcadeAssetsForTemplate(templateId?: string): ArcadeTemplateAssets {
  return (templateId && ASSETS[templateId as ArcadeTemplateAssetKey]) || DEFAULT_ASSETS;
}

export function arcadeAssetsForState(state: StudentGameState): ArcadeTemplateAssets {
  const configured = String(state.config?.template_id || state.template_id || "");
  return arcadeAssetsForTemplate(configured);
}
