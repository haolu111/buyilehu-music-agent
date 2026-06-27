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
        node.setConfigJson(toJson(config));
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