package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.response.LessonPlanResponse;
import com.buyilehu.musicagent.application.dto.response.LessonPlanSummaryResponse;
import com.buyilehu.musicagent.application.service.LessonPlanService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import java.util.List;
import javax.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@Validated
@RestController
@RequestMapping("/api/v1/lesson-plans")
public class LessonPlanController {
    private final LessonPlanService lessonPlanService;

    public LessonPlanController(LessonPlanService lessonPlanService) {
        this.lessonPlanService = lessonPlanService;
    }

    @PostMapping
    public ApiResponse<LessonPlanResponse> upload(@RequestParam("file") MultipartFile file,
                                                  @RequestParam(value = "title", required = false) String title) {
        return ApiResponse.success(lessonPlanService.upload(file, title));
    }

    @GetMapping("/mine")
    public ApiResponse<List<LessonPlanSummaryResponse>> listMine() {
        return ApiResponse.success(lessonPlanService.listMine());
    }

    @GetMapping("/{lessonPlanId}")
    public ApiResponse<LessonPlanResponse> getById(@PathVariable @Positive Long lessonPlanId) {
        return ApiResponse.success(lessonPlanService.getById(lessonPlanId));
    }
}
