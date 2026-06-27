package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityStep;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import java.util.Arrays;
import org.springframework.stereotype.Component;

@Component
public class ActivityChainGenerator {
    public ActivityChain generate(ParsedLesson parsedLesson, GeneratePreferences preferences) {
        ActivityChain chain = new ActivityChain();
        chain.setTitle(parsedLesson.getCourseName() + "互动课堂");
        chain.setSteps(Arrays.asList(
                new ActivityStep("课堂入口页", "entry", 1, Arrays.asList("scene_display", "lesson_title_card")),
                new ActivityStep("节拍体验工具", "meter_experience", 2, Arrays.asList("meter_compare", "beat_feedback")),
                new ActivityStep("节奏拖拽游戏", "rhythm_game", 3, Arrays.asList("rhythm_drag_game")),
                new ActivityStep("创编工作坊", "creation_workshop", 4, Arrays.asList("creation_panel")),
                new ActivityStep("展示总结页", "summary", 5, Arrays.asList("summary_page"))
        ));
        return chain;
    }
}
