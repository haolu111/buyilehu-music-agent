package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.LessonPlanResponse;
import org.springframework.web.multipart.MultipartFile;

public interface LessonPlanService {
    LessonPlanResponse upload(MultipartFile file, String title);

    LessonPlanResponse getById(Long lessonPlanId);
}
