package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.LearningEventRequest;
import com.buyilehu.musicagent.application.dto.request.StudentNodeSubmitRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.LearningEventResponse;
import com.buyilehu.musicagent.application.dto.response.StudentSubmissionResponse;
import com.buyilehu.musicagent.application.service.LearningEventService;
import com.buyilehu.musicagent.application.service.StudentProgressService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1")
public class StudentClassroomController {
    private final StudentProgressService studentProgressService;
    private final LearningEventService learningEventService;

    public StudentClassroomController(StudentProgressService studentProgressService,
                                      LearningEventService learningEventService) {
        this.studentProgressService = studentProgressService;
        this.learningEventService = learningEventService;
    }

    @GetMapping("/student/classrooms/current")
    public ApiResponse<ClassroomSessionResponse> getCurrentClassroom() {
        return ApiResponse.success(studentProgressService.getCurrentClassroom());
    }

    @GetMapping("/student/classroom-sessions/history")
    public ApiResponse<List<ClassroomSessionResponse>> listMyClassroomHistory() {
        return ApiResponse.success(studentProgressService.listMyClassroomHistory());
    }

    @GetMapping("/student/classroom-sessions/{sessionId}/submissions")
    public ApiResponse<List<StudentSubmissionResponse>> listMySubmissions(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(studentProgressService.listMySubmissions(sessionId));
    }

    @PostMapping("/student/classroom-sessions/{sessionId}/nodes/{nodeId}/enter")
    public ApiResponse<ClassroomSessionResponse> enterNode(@PathVariable @Positive Long sessionId,
                                                           @PathVariable @Positive Long nodeId) {
        return ApiResponse.success(studentProgressService.enterNode(sessionId, nodeId));
    }

    @PostMapping("/student/classroom-sessions/{sessionId}/nodes/{nodeId}/submit")
    public ApiResponse<ClassroomSessionResponse> submitNode(@PathVariable @Positive Long sessionId,
                                                            @PathVariable @Positive Long nodeId,
                                                            @Valid @RequestBody StudentNodeSubmitRequest request) {
        return ApiResponse.success(studentProgressService.submitNode(sessionId, nodeId, request));
    }

    @PostMapping("/learning-events")
    public ApiResponse<LearningEventResponse> recordLearningEvent(@Valid @RequestBody LearningEventRequest request) {
        return ApiResponse.success(learningEventService.record(request));
    }
}