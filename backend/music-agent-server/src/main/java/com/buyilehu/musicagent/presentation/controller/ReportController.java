package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.response.ClassroomReportResponse;
import com.buyilehu.musicagent.application.service.ReportService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/reports")
public class ReportController {
    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping("/classroom-sessions/{sessionId}")
    public ApiResponse<ClassroomReportResponse> getClassroomSessionReport(@PathVariable @Positive Long sessionId) {
        return ApiResponse.success(reportService.getClassroomSessionReport(sessionId));
    }
}