package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.ClassroomReportResponse;

public interface ReportService {
    ClassroomReportResponse getClassroomSessionReport(Long sessionId);
}