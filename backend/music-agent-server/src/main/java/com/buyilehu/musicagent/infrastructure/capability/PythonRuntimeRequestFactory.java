package com.buyilehu.musicagent.infrastructure.capability;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonRuntimeBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonPackageBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonPackageNodeBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonPackageDesignRequest;
import org.springframework.stereotype.Component;

@Component
public class PythonRuntimeRequestFactory {

    public PythonPackageDesignRequest buildDesign(ParsedLesson parsedLesson, GeneratePreferences preferences) {
        PythonPackageDesignRequest request = new PythonPackageDesignRequest();
        request.setLesson(buildLessonMap(parsedLesson));
        request.setPreferences(buildPreferencesMap(preferences));
        return request;
    }

    public PythonPackageBuildRequest buildPackage(
            ParsedLesson parsedLesson,
            GeneratePreferences preferences,
            List<ActivityNodeConfig> nodeConfigs,
            Map<String, String> activityIds
    ) {
        PythonPackageBuildRequest packageRequest = new PythonPackageBuildRequest();
        List<PythonPackageNodeBuildRequest> nodes = new ArrayList<PythonPackageNodeBuildRequest>();
        for (int index = 0; index < nodeConfigs.size(); index++) {
            ActivityNodeConfig nodeConfig = nodeConfigs.get(index);
            String clientRef = String.valueOf(index);
            String activityId = activityIds.get(clientRef);
            if (activityId == null || activityId.trim().isEmpty()) continue;
            PythonRuntimeBuildRequest single = build(parsedLesson, preferences, nodeConfig, activityId);
            PythonPackageNodeBuildRequest node = new PythonPackageNodeBuildRequest();
            node.setClientRef(clientRef);
            node.setActivityId(activityId);
            node.setComposition(single.getComposition());
            node.setRequest(single.getRequest());
            nodes.add(node);
        }
        packageRequest.setNodes(nodes);
        return packageRequest;
    }

    public PythonRuntimeBuildRequest build(
            ParsedLesson parsedLesson,
            GeneratePreferences preferences,
            ActivityNodeConfig nodeConfig,
            String activityId
    ) {
        PythonRuntimeBuildRequest request = new PythonRuntimeBuildRequest();
        request.setActivityId(activityId);
        request.setComposition(buildComposition(parsedLesson, preferences, nodeConfig, activityId));
        request.setRequest(buildRequest(parsedLesson, preferences, nodeConfig));
        return request;
    }

    private Map<String, Object> buildComposition(
            ParsedLesson parsedLesson,
            GeneratePreferences preferences,
            ActivityNodeConfig nodeConfig,
            String activityId
    ) {
        Map<String, Object> composition = new LinkedHashMap<String, Object>();
        composition.put("selected_activity_id", activityId);
        composition.put("selected_node_type", nodeConfig.getNodeType());
        composition.put("selected_node_title", nodeConfig.getTitle());
        composition.put("sort_order", nodeConfig.getSortOrder());
        composition.put("component_keys", new ArrayList<String>(safeList(nodeConfig.getComponentKeys())));
        composition.put("lesson_course_name", parsedLesson.getCourseName());
        composition.put("lesson_grade", parsedLesson.getGrade());
        composition.put("style", preferences == null ? null : preferences.getStyle());
        composition.put("duration_minutes", preferences == null ? null : preferences.getDurationMinutes());
        return composition;
    }

    private Map<String, Object> buildRequest(
            ParsedLesson parsedLesson,
            GeneratePreferences preferences,
            ActivityNodeConfig nodeConfig
    ) {
        Map<String, Object> request = new LinkedHashMap<String, Object>();
        request.put("lesson", buildLessonMap(parsedLesson));
        request.put("preferences", buildPreferencesMap(preferences));
        request.put("node", buildNodeMap(nodeConfig));
        return request;
    }

    private Map<String, Object> buildLessonMap(ParsedLesson parsedLesson) {
        Map<String, Object> lesson = new LinkedHashMap<String, Object>();
        lesson.put("course_name", parsedLesson.getCourseName());
        lesson.put("grade", parsedLesson.getGrade());
        lesson.put("objectives", new ArrayList<String>(safeList(parsedLesson.getObjectives())));
        lesson.put("key_points", new ArrayList<String>(safeList(parsedLesson.getKeyPoints())));
        lesson.put("process", new ArrayList<String>(safeList(parsedLesson.getProcess())));
        lesson.put("music_elements", new ArrayList<String>(safeList(parsedLesson.getMusicElements())));
        return lesson;
    }

    private Map<String, Object> buildPreferencesMap(GeneratePreferences preferences) {
        Map<String, Object> preferenceMap = new LinkedHashMap<String, Object>();
        if (preferences != null) {
            preferenceMap.put("style", preferences.getStyle());
            preferenceMap.put("duration_minutes", preferences.getDurationMinutes());
            preferenceMap.put("mode", preferences.getMode());
            preferenceMap.put("density", preferences.getDensity());
            preferenceMap.put("difficulty", preferences.getDifficulty());
            preferenceMap.put("flow", preferences.getFlow());
            preferenceMap.put("theme", preferences.getTheme());
        }
        return preferenceMap;
    }

    private Map<String, Object> buildNodeMap(ActivityNodeConfig nodeConfig) {
        Map<String, Object> node = new LinkedHashMap<String, Object>();
        node.put("title", nodeConfig.getTitle());
        node.put("node_type", nodeConfig.getNodeType());
        node.put("sort_order", nodeConfig.getSortOrder());
        node.put("component_keys", new ArrayList<String>(safeList(nodeConfig.getComponentKeys())));
        return node;
    }

    private <T> List<T> safeList(List<T> values) {
        return values == null ? new ArrayList<T>() : values;
    }
}
