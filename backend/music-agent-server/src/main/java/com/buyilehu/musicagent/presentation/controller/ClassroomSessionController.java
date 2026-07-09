package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.CreateClassroomSessionRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.StudentSubmissionResponse;
import com.buyilehu.musicagent.application.service.ClassroomSessionService;
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
@RequestMapping("/api/v1/classroom-sessions")
public class ClassroomSessionController {
    private final ClassroomSessionService classroomSessionService;

    public ClassroomSessionController(ClassroomSessionService classroomSessionService) {
        this.classroomSessionService = classroomSessionService;
    }

    @PostMapping
    public ApiResponse<ClassroomSessionResponse> create(@Valid @RequestBody CreateClassroomSessionRequest request) {
        return ApiResponse.success(classroomSessionService.create(request));
    }

    @GetMapping("/active")
    public ApiResponse<List<ClassroomSessionResponse>> listActiveForTeacher() {
        return ApiResponse.success(classroomSessionService.listActiveForTeacher());
    }

    @GetMapping("/{sessionId}")
    public ApiResponse<ClassroomSessionResponse> get(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(classroomSessionService.get(sessionId));
    }

    @GetMapping("/{sessionId}/submissions")
    public ApiResponse<List<StudentSubmissionResponse>> listSubmissions(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(classroomSessionService.listSubmissions(sessionId));
    }

    @PostMapping("/{sessionId}/start")
    public ApiResponse<ClassroomSessionResponse> start(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(classroomSessionService.start(sessionId));
    }

    @PostMapping("/{sessionId}/nodes/{nodeId}/unlock")
    public ApiResponse<ClassroomSessionResponse> unlockNode(@PathVariable @Positive Long sessionId,
                                                            @PathVariable @Positive Long nodeId) {
        return ApiResponse.success(classroomSessionService.unlockNode(sessionId, nodeId));
    }

    @PostMapping("/{sessionId}/pause")
    public ApiResponse<ClassroomSessionResponse> pause(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(classroomSessionService.pause(sessionId));
    }

    @PostMapping("/{sessionId}/end")
    public ApiResponse<ClassroomSessionResponse> end(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(classroomSessionService.end(sessionId));
    }
}