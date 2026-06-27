package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.CreateClassRequest;
import com.buyilehu.musicagent.application.dto.request.JoinClassRequest;
import com.buyilehu.musicagent.application.dto.response.ClassResponse;
import com.buyilehu.musicagent.application.dto.response.ClassStudentResponse;
import com.buyilehu.musicagent.application.service.ClassService;
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
@RequestMapping("/api/v1/classes")
public class ClassController {
    private final ClassService classService;

    public ClassController(ClassService classService) {
        this.classService = classService;
    }

    @PostMapping
    public ApiResponse<ClassResponse> create(@Valid @RequestBody CreateClassRequest request) {
        return ApiResponse.success(classService.create(request));
    }

    @GetMapping
    public ApiResponse<List<ClassResponse>> listMine() {
        return ApiResponse.success(classService.listMine());
    }

    @PostMapping("/join")
    public ApiResponse<ClassResponse> join(@Valid @RequestBody JoinClassRequest request) {
        return ApiResponse.success(classService.join(request));
    }

    @GetMapping("/{classId}/students")
    public ApiResponse<List<ClassStudentResponse>> listStudents(@PathVariable @Positive Long classId) {
        return ApiResponse.success(classService.listStudents(classId));
    }
}
