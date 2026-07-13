package com.buyilehu.musicagent.application.service.impl;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;

import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityClient;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityException;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityProperties;
import com.buyilehu.musicagent.infrastructure.capability.PythonRuntimeRequestFactory;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonRuntimeBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityRuntimeBuildData;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityRuntimeBuildResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.mock;

class PythonRuntimeIntegrationServiceImplTest {
    private final PythonCapabilityClient client = mock(PythonCapabilityClient.class);
    private final PythonRuntimeRequestFactory requestFactory = new PythonRuntimeRequestFactory();
    private final PythonCapabilityProperties properties = new PythonCapabilityProperties();
    private final ObjectMapper objectMapper = new ObjectMapper();
    private PythonRuntimeIntegrationServiceImpl service;

    @BeforeEach
    void setUp() {
        properties.setEnabled(true);
        properties.setCallMode(PythonCapabilityProperties.CallMode.SHADOW);
        properties.setNodeTypeActivityIdMappings(new LinkedHashMap<String, String>());
        properties.getNodeTypeActivityIdMappings().put("entry", "lesson_opening_hook");
        properties.getNodeTypeActivityIdMappings().put("summary", "exit_ticket_review");
        properties.getNodeTypeActivityIdMappings().put("creation_workshop", "xylophone_creation");
        service = new PythonRuntimeIntegrationServiceImpl(client, requestFactory, properties, objectMapper);
    }

    @Test
    void shouldEnrichNodeInShadowMode() throws Exception {
        ActivityNodeConfig nodeConfig = node("entry");
        PythonCapabilityRuntimeBuildResponse response = successResponse();
        when(client.buildRuntime(any(PythonRuntimeBuildRequest.class))).thenReturn(response);

        service.enrichNodes(sampleLesson(), samplePreferences(), Arrays.asList(nodeConfig));

        ArgumentCaptor<PythonRuntimeBuildRequest> captor = ArgumentCaptor.forClass(PythonRuntimeBuildRequest.class);
        verify(client).buildRuntime(captor.capture());
        assertThat(captor.getValue().getActivityId()).isEqualTo("lesson_opening_hook");
        assertThat(captor.getValue().getRequest()).containsKeys("lesson", "preferences", "node");
        assertThat(nodeConfig.getCapabilityActivityId()).isEqualTo("lesson_opening_hook");
        assertThat(nodeConfig.getCapabilitySource()).isEqualTo("python_shadow");
        assertThat(nodeConfig.getCapabilityStatus()).isEqualTo("shadow");
        assertThat(nodeConfig.getToolkit()).containsKey("selected");
        assertThat(nodeConfig.getRuntime()).containsEntry("runtime_status", "ready");
        assertThat(nodeConfig.getMediaSessionPreview()).isNull();
        assertThat(nodeConfig.getCapabilityError()).isNull();
    }

    @Test
    void shouldFallbackWhenNoMappingExists() {
        ActivityNodeConfig nodeConfig = node("unknown_node");

        service.enrichNodes(sampleLesson(), samplePreferences(), Arrays.asList(nodeConfig));

        verifyNoInteractions(client);
        assertThat(nodeConfig.getCapabilityActivityId()).isNull();
        assertThat(nodeConfig.getCapabilitySource()).isEqualTo("java_fallback");
        assertThat(nodeConfig.getCapabilityStatus()).isEqualTo("fallback");
        assertThat(nodeConfig.getCapabilityError().get("message").toString()).contains("No Python capability mapping");
    }

    @Test
    void shouldFallbackOnConnectionFailure() {
        ActivityNodeConfig nodeConfig = node("entry");
        when(client.buildRuntime(any(PythonRuntimeBuildRequest.class)))
                .thenThrow(new PythonCapabilityException(
                        PythonCapabilityException.ErrorType.CONNECTION_FAILED,
                        "Failed to connect to Python capability service for /api/v1/runtime/build"
                ));

        service.enrichNodes(sampleLesson(), samplePreferences(), Arrays.asList(nodeConfig));

        verify(client).buildRuntime(any(PythonRuntimeBuildRequest.class));
        assertThat(nodeConfig.getCapabilityActivityId()).isEqualTo("lesson_opening_hook");
        assertThat(nodeConfig.getCapabilitySource()).isEqualTo("java_fallback");
        assertThat(nodeConfig.getCapabilityStatus()).isEqualTo("fallback");
    }

    @Test
    void shouldFallbackOnNotFound() {
        ActivityNodeConfig nodeConfig = node("entry");
        when(client.buildRuntime(any(PythonRuntimeBuildRequest.class)))
                .thenThrow(new PythonCapabilityException(
                        PythonCapabilityException.ErrorType.CLIENT_ERROR,
                        "unknown activity template: lesson_opening_hook",
                        404,
                        "activity_not_found",
                        "unknown activity template: lesson_opening_hook",
                        null
                ));

        service.enrichNodes(sampleLesson(), samplePreferences(), Arrays.asList(nodeConfig));

        assertThat(nodeConfig.getCapabilitySource()).isEqualTo("java_fallback");
        assertThat(nodeConfig.getCapabilityStatus()).isEqualTo("fallback");
        assertThat(nodeConfig.getCapabilityError().get("message").toString()).contains("unknown activity template");
    }

    @Test
    void shouldHandlePartialSuccessAcrossMultipleNodes() throws Exception {
        ActivityNodeConfig first = node("entry");
        ActivityNodeConfig second = node("summary");
        PythonCapabilityRuntimeBuildResponse response = successResponse();
        when(client.buildRuntime(any(PythonRuntimeBuildRequest.class)))
                .thenReturn(response)
                .thenThrow(new PythonCapabilityException(
                        PythonCapabilityException.ErrorType.CLIENT_ERROR,
                        "unknown activity template: exit_ticket_review",
                        404,
                        "activity_not_found",
                        "unknown activity template: exit_ticket_review",
                        null
                ));

        service.enrichNodes(sampleLesson(), samplePreferences(), Arrays.asList(first, second));

        verify(client, times(2)).buildRuntime(any(PythonRuntimeBuildRequest.class));
        assertThat(first.getCapabilitySource()).isEqualTo("python_shadow");
        assertThat(first.getCapabilityStatus()).isEqualTo("shadow");
        assertThat(second.getCapabilitySource()).isEqualTo("java_fallback");
        assertThat(second.getCapabilityStatus()).isEqualTo("fallback");
        assertThat(second.getCapabilityError().get("message").toString()).contains("exit_ticket_review");
    }

    private ActivityNodeConfig node(String nodeType) {
        ActivityNodeConfig nodeConfig = new ActivityNodeConfig();
        nodeConfig.setTitle(nodeType + " title");
        nodeConfig.setNodeType(nodeType);
        nodeConfig.setSortOrder(1);
        nodeConfig.setComponentKeys(Arrays.asList("scene_display"));
        return nodeConfig;
    }

    private ParsedLesson sampleLesson() {
        ParsedLesson lesson = new ParsedLesson();
        lesson.setCourseName("旋律启蒙");
        lesson.setGrade("三年级");
        lesson.setObjectives(Arrays.asList("目标一"));
        lesson.setKeyPoints(Arrays.asList("要点一"));
        lesson.setProcess(Arrays.asList("导入"));
        lesson.setMusicElements(Arrays.asList("节奏"));
        return lesson;
    }

    private GeneratePreferences samplePreferences() {
        GeneratePreferences preferences = new GeneratePreferences();
        preferences.setStyle("playful");
        preferences.setDurationMinutes(30);
        return preferences;
    }

    private PythonCapabilityRuntimeBuildResponse successResponse() throws Exception {
        PythonCapabilityRuntimeBuildResponse response = new PythonCapabilityRuntimeBuildResponse();
        response.setSuccess(true);
        PythonCapabilityRuntimeBuildData data = new PythonCapabilityRuntimeBuildData();
        data.setActivityId("lesson_opening_hook");
        data.setToolkit(objectMapper.readTree("{\"selected\":{\"components\":[\"scene_display\"]}}"));
        data.setComposition(objectMapper.readTree("{\"selected_activity_id\":\"lesson_opening_hook\"}"));
        data.setRuntime(objectMapper.readTree("{\"runtime_status\":\"ready\",\"student_game_state\":{}}"));
        data.setMediaSessionPreview(null);
        response.setData(data);
        return response;
    }
}
