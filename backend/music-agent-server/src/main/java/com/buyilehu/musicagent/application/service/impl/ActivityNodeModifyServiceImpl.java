package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.application.service.ActivityNodeModifyService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class ActivityNodeModifyServiceImpl implements ActivityNodeModifyService {
    private final ObjectMapper objectMapper;

    public ActivityNodeModifyServiceImpl(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void applyNodeConfig(ActivityNode node, PackageNodeConfigUpdateRequest request) {
        if (request.getTitle() != null && !request.getTitle().trim().isEmpty()) {
            node.setTitle(request.getTitle().trim());
        }
        Map<String, Object> config = readJson(node.getConfigJson());
        putIfPresent(config, "description", request.getDescription());
        putIfPresent(config, "difficulty", request.getDifficulty());
        putIfPresent(config, "rhythmCardCount", request.getRhythmCardCount());
        putIfPresent(config, "hintEnabled", request.getHintEnabled());
        putIfPresent(config, "hidden", request.getHidden());
        if (request.getMusicContent() != null && !request.getMusicContent().isEmpty()) {
            config.put("musicContent", request.getMusicContent());
        }
        if (request.getResolvedMusicContent() != null && !request.getResolvedMusicContent().isEmpty()) {
            config.put("resolvedMusicContent", request.getResolvedMusicContent());
            patchActivityRuntime(config, request.getResolvedMusicContent());
        }
        node.setConfigJson(toJson(config));
    }

    @SuppressWarnings("unchecked")
    private void patchActivityRuntime(Map<String, Object> config, Map<String, Object> resolved) {
        Object runtimeValue = config.get("activityRuntime");
        if (!(runtimeValue instanceof Map)) return;
        Map<String, Object> runtime = (Map<String, Object>) runtimeValue;
        Object propsValue = runtime.get("props");
        Map<String, Object> props = propsValue instanceof Map
                ? (Map<String, Object>) propsValue : new HashMap<String, Object>();
        props.put("musicContent", resolved);
        copyResolvedList(props, resolved, "rhythm_patterns", "rhythmPatterns");
        copyResolvedList(props, resolved, "pitch_sets", "pitchSets");
        copyResolvedList(props, resolved, "melody_phrases", "melodyPhrases");
        copyResolvedList(props, resolved, "forms", "forms");
        copyResolvedList(props, resolved, "dynamics", "dynamics");
        copyResolvedList(props, resolved, "timbres", "timbres");
        List<Map<String, Object>> rhythmPatterns = mapList(resolved.get("rhythm_patterns"));
        if (!rhythmPatterns.isEmpty()) {
            List<Object> targetSequence = new java.util.ArrayList<Object>();
            for (Map<String, Object> pattern : rhythmPatterns) {
                Object tokens = pattern.get("tokens");
                if (tokens instanceof List) targetSequence.addAll((List<?>) tokens);
            }
            props.put("targetSequence", targetSequence);
        }
        List<Map<String, Object>> pitchSets = mapList(resolved.get("pitch_sets"));
        if (!pitchSets.isEmpty()) props.put("tokens", pitchSets.get(0).get("notes"));
        List<Map<String, Object>> melodies = mapList(resolved.get("melody_phrases"));
        if (!melodies.isEmpty()) {
            Object contour = melodies.get(0).get("contour");
            props.put("notes", contour == null ? melodies.get(0).get("notes") : contour);
        }
        List<Map<String, Object>> forms = mapList(resolved.get("forms"));
        if (!forms.isEmpty()) props.put("sections", forms.get(0).get("sections"));
        List<Map<String, Object>> timbres = mapList(resolved.get("timbres"));
        if (!timbres.isEmpty()) {
            List<Object> items = new java.util.ArrayList<Object>();
            for (Map<String, Object> timbre : timbres) items.add(timbre.get("label"));
            props.put("items", items);
            props.put("instrument", timbres.get(0).get("instrument"));
        }
        runtime.put("props", props);
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> mapList(Object value) {
        if (!(value instanceof List)) return java.util.Collections.emptyList();
        List<Map<String, Object>> result = new java.util.ArrayList<Map<String, Object>>();
        for (Object item : (List<?>) value) {
            if (item instanceof Map) result.add((Map<String, Object>) item);
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private void copyResolvedList(Map<String, Object> props, Map<String, Object> resolved,
                                  String sourceKey, String targetKey) {
        Object value = resolved.get(sourceKey);
        if (value instanceof java.util.List) props.put(targetKey, value);
    }

    private void putIfPresent(Map<String, Object> config, String key, Object value) {
        if (value != null) {
            config.put(key, value);
        }
    }

    private Map<String, Object> readJson(String json) {
        if (json == null || json.trim().isEmpty()) {
            return new HashMap<>();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {});
        } catch (Exception exception) {
            return new HashMap<>();
        }
    }

    private String toJson(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "node config is not valid json");
        }
    }
}
