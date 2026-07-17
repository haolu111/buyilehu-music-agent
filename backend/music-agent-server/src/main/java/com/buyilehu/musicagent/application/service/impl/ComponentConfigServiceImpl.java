package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.application.service.ComponentConfigService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ComponentInstance;
import com.buyilehu.musicagent.infrastructure.repository.ComponentInstanceRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class ComponentConfigServiceImpl implements ComponentConfigService {
    private final ComponentInstanceRepository componentInstanceRepository;
    private final ObjectMapper objectMapper;

    public ComponentConfigServiceImpl(ComponentInstanceRepository componentInstanceRepository, ObjectMapper objectMapper) {
        this.componentInstanceRepository = componentInstanceRepository;
        this.objectMapper = objectMapper;
    }

    @Override
    public void applyComponentConfig(ActivityNode node, PackageNodeConfigUpdateRequest request) {
        List<ComponentInstance> instances = componentInstanceRepository.findByActivityNodeIdOrderBySortOrderAsc(node.getId());
        if (instances.isEmpty()) {
            return;
        }
        ComponentInstance target = findTarget(instances, request.getComponentInstanceId());
        Map<String, Object> props = readJson(target.getPropsJson());
        if (request.getRhythmCardCount() != null) {
            props.put("rhythmCardCount", request.getRhythmCardCount());
        }
        if (request.getHintEnabled() != null) {
            props.put("hintEnabled", request.getHintEnabled());
        }
        if (request.getDifficulty() != null) {
            props.put("difficulty", request.getDifficulty());
        }
        if (request.getComponentParams() != null) {
            props.putAll(request.getComponentParams());
        }
        target.setPropsJson(toJson(props));
        componentInstanceRepository.save(target);
    }

    private ComponentInstance findTarget(List<ComponentInstance> instances, Long componentInstanceId) {
        if (componentInstanceId == null) {
            return instances.get(0);
        }
        for (ComponentInstance instance : instances) {
            if (componentInstanceId.equals(instance.getId())) {
                return instance;
            }
        }
        throw new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "component instance not found");
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
            throw new BusinessException(ErrorCode.BAD_REQUEST, "component config is not valid json");
        }
    }
}