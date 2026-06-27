package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.service.LessonParseService;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class LessonParseServiceImpl implements LessonParseService {
    private static final List<String> MUSIC_ELEMENT_KEYWORDS =
            Arrays.asList("节拍", "节奏", "旋律", "音色");

    @Override
    public String extractRawText(MultipartFile file) {
        String filename = file.getOriginalFilename();
        String lowerFilename = filename == null ? "" : filename.toLowerCase(Locale.ROOT);
        try {
            if (lowerFilename.endsWith(".docx")) {
                return extractDocx(file);
            }
            if (lowerFilename.endsWith(".txt")) {
                return new String(file.getBytes(), StandardCharsets.UTF_8);
            }
            if (lowerFilename.endsWith(".pdf")) {
                return "";
            }
            return new String(file.getBytes(), StandardCharsets.UTF_8);
        } catch (Exception exception) {
            return "";
        }
    }

    @Override
    public ParsedLesson parse(String rawText) {
        try {
            if (rawText == null || rawText.trim().isEmpty()) {
                return ParsedLesson.fallback();
            }

            ParsedLesson lesson = new ParsedLesson();
            lesson.setCourseName(extractCourseName(rawText));
            lesson.setGrade(extractGrade(rawText));
            lesson.setObjectives(extractSection(rawText, "教学目标"));
            lesson.setKeyPoints(extractSection(rawText, "教学重点"));
            lesson.setProcess(extractSection(rawText, "教学过程"));
            lesson.setMusicElements(extractMusicElements(rawText));
            return lesson;
        } catch (Exception exception) {
            return ParsedLesson.fallback();
        }
    }

    private String extractDocx(MultipartFile file) throws IOException {
        StringBuilder builder = new StringBuilder();
        try (XWPFDocument document = new XWPFDocument(file.getInputStream())) {
            for (XWPFParagraph paragraph : document.getParagraphs()) {
                String text = paragraph.getText();
                if (text != null && !text.trim().isEmpty()) {
                    builder.append(text.trim()).append('\n');
                }
            }
        }
        return builder.toString();
    }

    private String extractCourseName(String rawText) {
        for (String line : lines(rawText)) {
            String normalized = line.trim();
            if (normalized.startsWith("课程名称") || normalized.startsWith("课题") || normalized.startsWith("课名")) {
                return valueAfterSeparator(normalized);
            }
        }
        String firstLine = firstMeaningfulLine(rawText);
        return firstLine == null ? "未识别课程名" : limit(firstLine, 60);
    }

    private String extractGrade(String rawText) {
        for (String line : lines(rawText)) {
            String normalized = line.trim();
            if (normalized.contains("年级")) {
                return limit(valueAfterSeparator(normalized), 30);
            }
        }
        return "未识别年级";
    }

    private List<String> extractSection(String rawText, String title) {
        List<String> result = new ArrayList<>();
        String[] lines = lines(rawText);
        boolean collecting = false;
        for (String line : lines) {
            String normalized = line.trim();
            if (normalized.isEmpty()) {
                continue;
            }
            if (normalized.contains(title)) {
                collecting = true;
                String inline = valueAfterSeparator(normalized);
                if (!inline.equals(normalized) && !inline.isEmpty()) {
                    result.add(inline);
                }
                continue;
            }
            if (collecting && isAnotherSection(normalized, title)) {
                break;
            }
            if (collecting) {
                result.add(stripListPrefix(normalized));
            }
        }
        return result;
    }

    private List<String> extractMusicElements(String rawText) {
        List<String> result = new ArrayList<>();
        for (String keyword : MUSIC_ELEMENT_KEYWORDS) {
            if (rawText.contains(keyword)) {
                result.add(keyword);
            }
        }
        return result;
    }

    private boolean isAnotherSection(String line, String currentTitle) {
        List<String> sectionTitles = Arrays.asList("教学目标", "教学重点", "教学难点", "教学准备", "教学过程", "课堂小结");
        for (String sectionTitle : sectionTitles) {
            if (!sectionTitle.equals(currentTitle) && line.contains(sectionTitle)) {
                return true;
            }
        }
        return false;
    }

    private String[] lines(String rawText) {
        return rawText.replace("\r\n", "\n").replace('\r', '\n').split("\n");
    }

    private String firstMeaningfulLine(String rawText) {
        for (String line : lines(rawText)) {
            if (!line.trim().isEmpty()) {
                return line.trim();
            }
        }
        return null;
    }

    private String valueAfterSeparator(String line) {
        int colonIndex = Math.max(line.indexOf('：'), line.indexOf(':'));
        if (colonIndex >= 0 && colonIndex + 1 < line.length()) {
            return line.substring(colonIndex + 1).trim();
        }
        return line.trim();
    }

    private String stripListPrefix(String line) {
        return line.replaceFirst("^[0-9一二三四五六七八九十]+[、.．)]\\s*", "").trim();
    }

    private String limit(String value, int maxLength) {
        if (value == null) {
            return "";
        }
        return value.length() <= maxLength ? value : value.substring(0, maxLength);
    }
}
