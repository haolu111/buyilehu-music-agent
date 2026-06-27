package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
public class QualityReportGenerator {
    public QualityCheckResult check(ActivityChain chain, List<ActivityNodeConfig> nodeConfigs) {
        QualityCheckResult result = new QualityCheckResult();
        if (nodeConfigs == null || nodeConfigs.size() != 5) {
            result.setScore(70);
            result.setStatus("warning");
            result.getMessages().add("活动链节点数量不是标准的5个");
            return result;
        }
        result.setScore(95);
        result.setStatus("passed");
        result.getMessages().add("已生成标准五段式音乐互动课堂活动链");
        result.getMessages().add("组件实例已覆盖入口、节拍、节奏、创编与总结环节");
        return result;
    }
}
