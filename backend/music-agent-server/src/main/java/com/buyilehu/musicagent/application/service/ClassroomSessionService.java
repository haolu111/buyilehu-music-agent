package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.CreateClassroomSessionRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;

public interface ClassroomSessionService {
    ClassroomSessionResponse create(CreateClassroomSessionRequest request);

    ClassroomSessionResponse get(Long sessionId);

    ClassroomSessionResponse start(Long sessionId);

    ClassroomSessionResponse unlockNode(Long sessionId, Long nodeId);

    ClassroomSessionResponse pause(Long sessionId);

    ClassroomSessionResponse end(Long sessionId);
}
