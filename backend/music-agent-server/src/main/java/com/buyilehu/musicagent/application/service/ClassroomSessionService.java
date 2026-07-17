package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.CreateClassroomSessionRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.StudentSubmissionResponse;
import java.util.List;

public interface ClassroomSessionService {
    ClassroomSessionResponse create(CreateClassroomSessionRequest request);

    ClassroomSessionResponse get(Long sessionId);

    List<ClassroomSessionResponse> listActiveForTeacher();

    List<StudentSubmissionResponse> listSubmissions(Long sessionId);

    ClassroomSessionResponse start(Long sessionId);

    ClassroomSessionResponse unlockNode(Long sessionId, Long nodeId);

    ClassroomSessionResponse pause(Long sessionId);

    ClassroomSessionResponse end(Long sessionId);
}