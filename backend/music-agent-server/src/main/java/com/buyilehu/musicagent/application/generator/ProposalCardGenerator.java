package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityStep;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class ProposalCardGenerator {
    public String generate(ActivityChain chain, QualityCheckResult quality) {
        String activities = chain.getSteps().stream()
                .map(ActivityStep::getTitle)
                .collect(Collectors.joining(" -> "));
        StringBuilder content = new StringBuilder()
                .append("生成方案：").append(chain.getTitle())
                .append("\n活动结构：").append(activities)
                .append("\n设计来源：").append(providerLabel(chain.getDesignProvider()));
        if (StringUtils.hasText(chain.getDesignModel())) {
            content.append(" / ").append(chain.getDesignModel());
        }
        if (StringUtils.hasText(chain.getReasoningSummary())) {
            content.append("\n设计依据：").append(chain.getReasoningSummary());
        }
        if (StringUtils.hasText(chain.getDesignFallbackReason())) {
            content.append("\n降级信息：").append(chain.getDesignFallbackReason());
        }
        if (StringUtils.hasText(chain.getDesignTraceId())) {
            content.append("\n设计追踪号：").append(chain.getDesignTraceId());
        }
        return content.append("\n质量评分：").append(quality.getScore()).toString();
    }

    private String providerLabel(String provider) {
        if ("chat_ecnu".equals(provider)) return "ECNU 大模型 Agent";
        if ("doubao".equals(provider)) return "豆包备用模型 Agent";
        if ("rule_fallback".equals(provider)) return "Python 本地规则降级";
        if ("java_rule_fallback".equals(provider)) return "Java 固定规则降级";
        return StringUtils.hasText(provider) ? provider : "未知";
    }
}
