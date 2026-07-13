package com.buyilehu.musicagent.application.service.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.buyilehu.musicagent.application.service.PythonRuntimeIntegrationService;
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
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class PythonRuntimeIntegrationServiceImpl implements PythonRuntimeIntegrationService {
    private final PythonCapabilityClient pythonCapabilityClient;
    private final PythonRuntimeRequestFactory requestFactory;
    private final PythonCapabilityProperties properties;
    private final ObjectMapper objectMapper;

    public PythonRuntimeIntegrationServiceImpl(
            PythonCapabilityClient pythonCapabilityClient,
            PythonRuntimeRequestFactory requestFactory,
            PythonCapabilityProperties properties,
            ObjectMapper objectMapper
    ) {
        this.pythonCapabilityClient = pythonCapabilityClient;
        this.requestFactory = requestFactory;
        this.properties = properties;
        this.objectMapper = objectMapper;
    }

    @Override
    public void enrichNodes(ParsedLesson parsedLesson, GeneratePreferences preferences, List<ActivityNodeConfig> nodeConfigs) {
        if (nodeConfigs == null || nodeConfigs.isEmpty()) {
            return;
        }
        PythonCapabilityProperties.CallMode callMode = resolveCallMode();
        for (ActivityNodeConfig nodeConfig : nodeConfigs) {
            enrichNode(parsedLesson, preferences, nodeConfig, callMode);
        }
    }

    private void enrichNode(
            ParsedLesson parsedLesson,
            GeneratePreferences preferences,
            ActivityNodeConfig nodeConfig,
            PythonCapabilityProperties.CallMode callMode
    ) {
        String activityId = resolveActivityId(nodeConfig);
        if (!StringUtils.hasText(activityId) || callMode == PythonCapabilityProperties.CallMode.DISABLED) {
            applyFallback(nodeConfig, activityId, callMode == PythonCapabilityProperties.CallMode.DISABLED
                    ? "Python capability integration is disabled."
                    : "No Python capability mapping for nodeType=" + nodeConfig.getNodeType());
            return;
        }

        try {
            PythonRuntimeBuildRequest request = requestFactory.build(parsedLesson, preferences, nodeConfig, activityId);
            PythonCapabilityRuntimeBuildResponse response = pythonCapabilityClient.buildRuntime(request);
            if (response == null || !response.isSuccess() || response.getData() == null) {
                throw new PythonCapabilityException(
                        PythonCapabilityException.ErrorType.RESPONSE_PARSE_ERROR,
                        "Python runtime response missing success/data wrapper for activity_id=" + activityId
                );
            }
            applySuccess(nodeConfig, activityId, callMode, response.getData());
        } catch (PythonCapabilityException exception) {
            applyFallback(nodeConfig, activityId, shortMessage(exception));
        } catch (RuntimeException exception) {
            applyFallback(nodeConfig, activityId, shortMessage(exception));
        }
    }

    private void applySuccess(
            ActivityNodeConfig nodeConfig,
            String activityId,
            PythonCapabilityProperties.CallMode callMode,
            PythonCapabilityRuntimeBuildData data
    ) {
        nodeConfig.setCapabilityActivityId(activityId);
        nodeConfig.setCapabilitySource(callMode == PythonCapabilityProperties.CallMode.PRIMARY ? "python_primary" : "python_shadow");
        nodeConfig.setCapabilityStatus(callMode == PythonCapabilityProperties.CallMode.PRIMARY ? "primary" : "shadow");
        nodeConfig.setToolkit(convertNodeToMap(data.getToolkit()));
        nodeConfig.setRuntime(convertNodeToMap(data.getRuntime()));
        nodeConfig.setMediaSessionPreview(convertNullableNodeToMap(data.getMediaSessionPreview()));
        nodeConfig.setCapabilityError(null);
    }

    private void applyFallback(ActivityNodeConfig nodeConfig, String activityId, String message) {
        nodeConfig.setCapabilityActivityId(StringUtils.hasText(activityId) ? activityId : null);
        nodeConfig.setCapabilitySource("java_fallback");
        nodeConfig.setCapabilityStatus("fallback");
        nodeConfig.setCapabilityError(buildErrorMap(message));
        nodeConfig.setToolkit(new HashMap<String, Object>());
        nodeConfig.setRuntime(new HashMap<String, Object>());
        nodeConfig.setMediaSessionPreview(null);
    }

    private Map<String, Object> buildErrorMap(String message) {
        Map<String, Object> error = new java.util.LinkedHashMap<String, Object>();
        error.put("message", shorten(message));
        return error;
    }

    private PythonCapabilityProperties.CallMode resolveCallMode() {
        if (!properties.isEnabled()) {
            return PythonCapabilityProperties.CallMode.DISABLED;
        }
        PythonCapabilityProperties.CallMode callMode = properties.getCallMode();
        return callMode == null ? PythonCapabilityProperties.CallMode.SHADOW : callMode;
    }

    private String resolveActivityId(ActivityNodeConfig nodeConfig) {
        if (nodeConfig == null || nodeConfig.getNodeType() == null) {
            return null;
        }
        Map<String, String> mappings = properties.getNodeTypeActivityIdMappings();
        if (mappings == null || mappings.isEmpty()) {
            return null;
        }
        String mapped = mappings.get(nodeConfig.getNodeType());
        return StringUtils.hasText(mapped) ? mapped.trim() : null;
    }

    private Map<String, Object> convertNodeToMap(JsonNode node) {
        if (node == null || node.isNull()) {
            return new HashMap<String, Object>();
        }
        return objectMapper.convertValue(node, new TypeReference<Map<String, Object>>() {});
    }

    private Map<String, Object> convertNullableNodeToMap(JsonNode node) {
        if (node == null || node.isNull()) {
            return null;
        }
        return objectMapper.convertValue(node, new TypeReference<Map<String, Object>>() {});
    }

    private String shortMessage(Throwable throwable) {
        if (throwable == null || !StringUtils.hasText(throwable.getMessage())) {
            return "Python runtime integration failed.";
        }
        return shorten(throwable.getMessage());
    }

    private String shorten(String message) {
        if (!StringUtils.hasText(message)) {
            return "Python runtime integration failed.";
        }
        String compact = message.trim().replace('\n', ' ');
        return compact.length() <= 160 ? compact : compact.substring(0, 157) + "...";
    }
}
