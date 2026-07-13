package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.ActivityStep;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
public class ComponentMatcher {
    public List<ActivityNodeConfig> match(ActivityChain chain, ParsedLesson parsedLesson) {
        List<ActivityNodeConfig> configs = new ArrayList<>();
        for (ActivityStep step : chain.getSteps()) {
            ActivityNodeConfig config = new ActivityNodeConfig();
            config.setTitle(step.getTitle());
            config.setCapabilityActivityId(step.getActivityId());
            config.setNodeType(step.getNodeType());
            config.setSortOrder(step.getSortOrder());
            config.setComponentKeys(new ArrayList<>(step.getComponentKeys()));
            configs.add(config);
        }
        return configs;
    }
}
