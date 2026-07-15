package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.CreateClassRequest;
import com.buyilehu.musicagent.application.dto.request.JoinClassRequest;
import com.buyilehu.musicagent.application.dto.response.ClassResponse;
import com.buyilehu.musicagent.application.dto.response.ClassStudentResponse;

import java.util.List;

public interface ClassService {
    ClassResponse create(CreateClassRequest request);

    List<ClassResponse> listMine();

    ClassResponse join(JoinClassRequest request);

    List<ClassStudentResponse> listStudents(Long classId);
}
