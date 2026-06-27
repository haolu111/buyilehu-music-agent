package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.StudentNodeSubmitRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;

public interface StudentProgressService {
    ClassroomSessionResponse getCurrentClassroom();

    ClassroomSessionResponse enterNode(Long sessionId, Long nodeId);

    ClassroomSessionResponse submitNode(Long sessionId, Long nodeId, StudentNodeSubmitRequest request);
}
