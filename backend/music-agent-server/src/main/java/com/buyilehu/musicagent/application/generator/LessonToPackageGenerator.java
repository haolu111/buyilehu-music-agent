package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import org.springframework.stereotype.Component;

@Component
public class LessonToPackageGenerator {
    private final ActivityChainGenerator activityChainGenerator;

    public LessonToPackageGenerator(ActivityChainGenerator activityChainGenerator) {
        this.activityChainGenerator = activityChainGenerator;
    }

    public ActivityChain generate(ParsedLesson parsedLesson, GeneratePreferences preferences) {
        return activityChainGenerator.generate(parsedLesson, preferences);
    }
}
