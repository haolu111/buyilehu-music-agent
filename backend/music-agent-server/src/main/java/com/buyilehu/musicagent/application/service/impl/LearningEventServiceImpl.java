package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.LearningEventRequest;
import com.buyilehu.musicagent.application.dto.response.LearningEventResponse;
import com.buyilehu.musicagent.application.service.LearningEventService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.LearningEvent;
import com.buyilehu.musicagent.infrastructure.repository.LearningEventRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class LearningEventServiceImpl implements LearningEventService {
    private final LearningEventRepository learningEventRepository;
    private final ObjectMapper objectMapper;

    public LearningEventServiceImpl(LearningEventRepository learningEventRepository, ObjectMapper objectMapper) {
        this.learningEventRepository = learningEventRepository;
        this.objectMapper = objectMapper;
    }

    @Override
    @Transactional
    public LearningEventResponse record(LearningEventRequest request) {
        return recordNodeEvent(request.getSessionId(), getCurrentUserId(), request.getActivityNodeId(),
                request.getEventType(), request.getEventData());
    }

    @Override
    @Transactional
    public LearningEventResponse recordNodeEvent(Long sessionId, Long studentId, Long nodeId,
                                                 String eventType, Map<String, Object> eventData) {
        LearningEvent event = new LearningEvent();
        event.setSessionId(sessionId);
        event.setStudentId(studentId);
        event.setActivityNodeId(nodeId);
        event.setEventType(eventType);
        event.setEventData(toJson(eventData));
        event.setOccurredAt(LocalDateTime.now());
        return LearningEventResponse.from(learningEventRepository.save(event));
    }

    private String toJson(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "event data is not valid json");
        }
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
    }
}
