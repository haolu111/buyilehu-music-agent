package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.PackageResponse;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.LessonPlan;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import java.util.List;

public interface PackageService {
    InteractivePackage createPackage(LessonPlan lessonPlan, ParsedLesson parsedLesson, Long generationJobId);

    PackageResponse getPackage(Long packageId);

    List<PackageResponse> listMyPackages();
}
