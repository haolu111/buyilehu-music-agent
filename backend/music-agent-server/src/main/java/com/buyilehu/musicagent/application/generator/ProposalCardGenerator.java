package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import org.springframework.stereotype.Component;

@Component
public class ProposalCardGenerator {
    public String generate(ActivityChain chain, QualityCheckResult quality) {
        return "生成方案：" + chain.getTitle()
                + "\n活动结构：课堂入口页 → 节拍体验工具 → 节奏拖拽游戏 → 创编工作坊 → 展示总结页"
                + "\n质量评分：" + quality.getScore()
                + "\n建议：教师可根据课堂时长调整节奏拖拽游戏和创编工作坊的练习次数。";
    }
}
