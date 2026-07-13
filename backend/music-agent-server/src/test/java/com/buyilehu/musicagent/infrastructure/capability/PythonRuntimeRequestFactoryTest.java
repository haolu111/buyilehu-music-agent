package com.buyilehu.musicagent.infrastructure.capability;

import java.util.Arrays;
import java.util.Map;

import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonRuntimeBuildRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class PythonRuntimeRequestFactoryTest {
    private final PythonRuntimeRequestFactory factory = new PythonRuntimeRequestFactory();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void shouldBuildRequestWithRequestField() throws Exception {
        ParsedLesson lesson = new ParsedLesson();
        lesson.setCourseName("旋律启蒙");
        lesson.setGrade("三年级");
        lesson.setObjectives(Arrays.asList("目标一"));
        lesson.setKeyPoints(Arrays.asList("要点一"));
        lesson.setProcess(Arrays.asList("导入"));
        lesson.setMusicElements(Arrays.asList("节奏"));

        GeneratePreferences preferences = new GeneratePreferences();
        preferences.setStyle("playful");
        preferences.setDurationMinutes(30);

        ActivityNodeConfig nodeConfig = new ActivityNodeConfig();
        nodeConfig.setTitle("课堂入口");
        nodeConfig.setNodeType("entry");
        nodeConfig.setSortOrder(1);
        nodeConfig.setComponentKeys(Arrays.asList("scene_display", "lesson_title_card"));

        PythonRuntimeBuildRequest request = factory.build(lesson, preferences, nodeConfig, "lesson_opening_hook");
        String json = objectMapper.writeValueAsString(request);

        assertThat(request.getActivityId()).isEqualTo("lesson_opening_hook");
        assertThat(request.getComposition()).containsEntry("selected_activity_id", "lesson_opening_hook");
        assertThat(((Map<?, ?>) request.getRequest().get("lesson")).get("course_name")).isEqualTo("旋律启蒙");
        assertThat(json).contains("\"request\"");
        assertThat(json).doesNotContain("request_payload");
    }
}
