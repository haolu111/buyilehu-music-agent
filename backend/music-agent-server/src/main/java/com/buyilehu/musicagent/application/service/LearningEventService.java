package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.LearningEventRequest;
import com.buyilehu.musicagent.application.dto.response.LearningEventResponse;
import java.util.Map;

public interface LearningEventService {
    LearningEventResponse record(LearningEventRequest request);

    LearningEventResponse recordNodeEvent(Long sessionId, Long studentId, Long nodeId, String eventType, Map<String, Object> eventData);
}
