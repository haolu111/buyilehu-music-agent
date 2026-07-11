package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.StudentNodeSubmitRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.StudentSubmissionResponse;
import java.util.List;

public interface StudentProgressService {
    ClassroomSessionResponse getCurrentClassroom();

    List<ClassroomSessionResponse> listMyClassroomHistory();

    List<StudentSubmissionResponse> listMySubmissions(Long sessionId);

    ClassroomSessionResponse enterNode(Long sessionId, Long nodeId);

    ClassroomSessionResponse submitNode(Long sessionId, Long nodeId, StudentNodeSubmitRequest request);
}