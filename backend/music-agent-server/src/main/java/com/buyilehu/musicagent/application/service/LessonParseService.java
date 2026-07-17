package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.domain.model.ParsedLesson;
import org.springframework.web.multipart.MultipartFile;

public interface LessonParseService {
    String extractRawText(MultipartFile file);

    ParsedLesson parse(String rawText);
}
