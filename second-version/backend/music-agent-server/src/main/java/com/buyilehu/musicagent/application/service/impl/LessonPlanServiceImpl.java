package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.response.LessonPlanResponse;
import com.buyilehu.musicagent.application.dto.response.LessonPlanSummaryResponse;
import com.buyilehu.musicagent.application.service.LessonParseService;
import com.buyilehu.musicagent.application.service.LessonPlanService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.LessonPlan;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.repository.LessonPlanRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import com.buyilehu.musicagent.infrastructure.storage.FileStorageService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class LessonPlanServiceImpl implements LessonPlanService {
    private static final Logger log = LoggerFactory.getLogger(LessonPlanServiceImpl.class);
    private static final String PARSE_SUCCESS = "success";
    private static final String STATUS_UPLOADED = "uploaded";

    private final LessonPlanRepository lessonPlanRepository;
    private final UserRepository userRepository;
    private final FileStorageService fileStorageService;
    private final LessonParseService lessonParseService;
    private final ObjectMapper objectMapper;

    public LessonPlanServiceImpl(LessonPlanRepository lessonPlanRepository,
                                 UserRepository userRepository,
                                 FileStorageService fileStorageService,
                                 LessonParseService lessonParseService,
                                 ObjectMapper objectMapper) {
        this.lessonPlanRepository = lessonPlanRepository;
        this.userRepository = userRepository;
        this.fileStorageService = fileStorageService;
        this.lessonParseService = lessonParseService;
        this.objectMapper = objectMapper;
    }

    @Override
    @Transactional
    public LessonPlanResponse upload(MultipartFile file, String title) {
        User currentUser = getCurrentUser();
        ensureTeacher(currentUser);
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ErrorCode.PARAM_ERROR, "请上传教案文件");
        }

        String sourceFileUrl;
        try {
            sourceFileUrl = fileStorageService.store("lesson-plans", file.getOriginalFilename(), file.getInputStream());
        } catch (Exception exception) {
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "教案文件保存失败");
        }

        String rawText = lessonParseService.extractRawText(file);
        ParsedLesson parsedLesson = lessonParseService.parse(rawText);

        LessonPlan lessonPlan = new LessonPlan();
        lessonPlan.setTeacherId(currentUser.getId());
        lessonPlan.setTitle(resolveTitle(title, file, parsedLesson));
        lessonPlan.setSourceFileUrl(sourceFileUrl);
        lessonPlan.setRawText(rawText);
        lessonPlan.setParsedJson(toJson(parsedLesson));
        lessonPlan.setParseStatus(PARSE_SUCCESS);
        lessonPlan.setStatus(STATUS_UPLOADED);

        LessonPlan savedLessonPlan = lessonPlanRepository.save(lessonPlan);
        log.info("Lesson plan uploaded: lessonPlanId={}, teacherId={}, title={}",
                savedLessonPlan.getId(), savedLessonPlan.getTeacherId(), savedLessonPlan.getTitle());
        return LessonPlanResponse.from(savedLessonPlan);
    }

    @Override
    @Transactional(readOnly = true)
    public LessonPlanResponse getById(Long lessonPlanId) {
        User currentUser = getCurrentUser();
        LessonPlan lessonPlan = lessonPlanRepository.findById(lessonPlanId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "教案不存在"));
        if (!currentUser.getId().equals(lessonPlan.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能查看自己的教案");
        }
        return LessonPlanResponse.from(lessonPlan);
    }

    @Override
    @Transactional(readOnly = true)
    public List<LessonPlanSummaryResponse> listMine() {
        User currentUser = getCurrentUser();
        List<LessonPlanSummaryResponse> lessonPlans = lessonPlanRepository.findByTeacherIdOrderByIdDesc(currentUser.getId())
                .stream()
                .map(LessonPlanSummaryResponse::from)
                .collect(Collectors.toList());
        log.info("Lesson plans queried: teacherId={}, count={}", currentUser.getId(), lessonPlans.size());
        return lessonPlans;
    }

    private String resolveTitle(String title, MultipartFile file, ParsedLesson parsedLesson) {
        if (title != null && !title.trim().isEmpty()) {
            return title.trim();
        }
        if (parsedLesson.getCourseName() != null && !"未识别课程名".equals(parsedLesson.getCourseName())) {
            return parsedLesson.getCourseName();
        }
        String filename = file.getOriginalFilename();
        if (filename != null && !filename.trim().isEmpty()) {
            int dotIndex = filename.lastIndexOf('.');
            return dotIndex > 0 ? filename.substring(0, dotIndex) : filename;
        }
        return "未命名教案";
    }

    private String toJson(ParsedLesson parsedLesson) {
        try {
            return objectMapper.writeValueAsString(parsedLesson);
        } catch (JsonProcessingException exception) {
            try {
                return objectMapper.writeValueAsString(ParsedLesson.fallback());
            } catch (JsonProcessingException ignored) {
                return "{\"courseName\":\"未识别课程名\",\"grade\":\"未识别年级\",\"objectives\":[],\"keyPoints\":[],\"process\":[]}";
            }
        }
    }

    private User getCurrentUser() {
        return userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "登录用户不存在"));
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
    }

    private void ensureTeacher(User user) {
        if (user.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只有教师可以上传教案");
        }
    }
}
