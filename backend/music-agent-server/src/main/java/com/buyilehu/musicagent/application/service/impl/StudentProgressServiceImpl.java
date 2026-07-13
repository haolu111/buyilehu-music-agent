package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.StudentNodeSubmitRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.SessionNodeStateResponse;
import com.buyilehu.musicagent.application.dto.response.StudentSubmissionResponse;
import com.buyilehu.musicagent.application.service.LearningEventService;
import com.buyilehu.musicagent.application.service.StudentProgressService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ClassMember;
import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import com.buyilehu.musicagent.domain.entity.PackagePublication;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import com.buyilehu.musicagent.domain.entity.StudentProgress;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassMemberRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassroomSessionRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackagePublicationRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.SessionNodeStateRepository;
import com.buyilehu.musicagent.infrastructure.repository.StudentProgressRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityClient;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonActivityAssessmentRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityAssessmentResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class StudentProgressServiceImpl implements StudentProgressService {
    private final ClassroomSessionRepository classroomSessionRepository;
    private final PackagePublicationRepository packagePublicationRepository;
    private final PackageVersionRepository packageVersionRepository;
    private final SessionNodeStateRepository sessionNodeStateRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final ClassMemberRepository classMemberRepository;
    private final StudentProgressRepository studentProgressRepository;
    private final UserRepository userRepository;
    private final LearningEventService learningEventService;
    private final ObjectMapper objectMapper;
    private final PythonCapabilityClient pythonCapabilityClient;

    public StudentProgressServiceImpl(ClassroomSessionRepository classroomSessionRepository,
                                      PackagePublicationRepository packagePublicationRepository,
                                      PackageVersionRepository packageVersionRepository,
                                      SessionNodeStateRepository sessionNodeStateRepository,
                                      ActivityNodeRepository activityNodeRepository,
                                      ClassMemberRepository classMemberRepository,
                                      StudentProgressRepository studentProgressRepository,
                                      UserRepository userRepository,
                                      LearningEventService learningEventService,
                                      ObjectMapper objectMapper,
                                      PythonCapabilityClient pythonCapabilityClient) {
        this.classroomSessionRepository = classroomSessionRepository;
        this.packagePublicationRepository = packagePublicationRepository;
        this.packageVersionRepository = packageVersionRepository;
        this.sessionNodeStateRepository = sessionNodeStateRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.classMemberRepository = classMemberRepository;
        this.studentProgressRepository = studentProgressRepository;
        this.userRepository = userRepository;
        this.learningEventService = learningEventService;
        this.objectMapper = objectMapper;
        this.pythonCapabilityClient = pythonCapabilityClient;
    }

    @Override
    @Transactional(readOnly = true)
    public ClassroomSessionResponse getCurrentClassroom() {
        User student = getCurrentStudent();
        List<ClassMember> memberships = classMemberRepository.findByUserIdAndStatusOrderByIdDesc(student.getId(), "active");
        if (memberships.isEmpty()) {
            return null;
        }
        List<Long> classIds = new ArrayList<>();
        for (ClassMember membership : memberships) {
            classIds.add(membership.getClassId());
        }
        List<ClassroomSession> sessions = classroomSessionRepository.findByClassIdInAndStatusInOrderByIdDesc(
                classIds, Arrays.asList("running", "paused"));
        for (ClassroomSession session : sessions) {
            if (isPublicationActive(session)) {
                return buildResponse(session);
            }
        }
        return null;
    }



    @Override
    @Transactional(readOnly = true)
    public List<ClassroomSessionResponse> listMyClassroomHistory() {
        User student = getCurrentStudent();
        List<ClassMember> memberships = classMemberRepository.findByUserIdAndStatusOrderByIdDesc(student.getId(), "active");
        if (memberships.isEmpty()) {
            return Collections.emptyList();
        }
        List<Long> classIds = new ArrayList<>();
        for (ClassMember membership : memberships) {
            classIds.add(membership.getClassId());
        }
        List<ClassroomSession> sessions = classroomSessionRepository.findByClassIdInAndStatusInOrderByIdDesc(
                classIds, Arrays.asList("running", "paused", "ended"));
        List<ClassroomSessionResponse> responses = new ArrayList<>();
        for (ClassroomSession session : sessions) {
            if (isPublicationActive(session)) {
                responses.add(buildResponse(session));
            }
        }
        return responses;
    }

    @Override
    @Transactional(readOnly = true)
    public List<StudentSubmissionResponse> listMySubmissions(Long sessionId) {
        User student = getCurrentStudent();
        ClassroomSession session = classroomSessionRepository.findById(sessionId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session not found"));
        if (!classMemberRepository.existsByClassIdAndUserIdAndStatus(session.getClassId(), student.getId(), "active")) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "student is not in this class");
        }
        List<StudentProgress> progressList = studentProgressRepository.findBySessionIdAndStudentId(sessionId, student.getId());
        List<Long> nodeIds = new ArrayList<>();
        for (StudentProgress progress : progressList) {
            if (progress.getCurrentNodeId() != null) {
                nodeIds.add(progress.getCurrentNodeId());
            }
        }
        Map<Long, ActivityNode> nodesById = new HashMap<>();
        if (!nodeIds.isEmpty()) {
            for (ActivityNode node : activityNodeRepository.findByIdIn(nodeIds)) {
                nodesById.put(node.getId(), node);
            }
        }
        List<StudentSubmissionResponse> responses = new ArrayList<>();
        for (StudentProgress progress : progressList) {
            responses.add(StudentSubmissionResponse.from(progress, student, nodesById.get(progress.getCurrentNodeId())));
        }
        Collections.sort(responses, new Comparator<StudentSubmissionResponse>() {
            @Override
            public int compare(StudentSubmissionResponse left, StudentSubmissionResponse right) {
                Integer leftOrder = left.getSortOrder() == null ? Integer.MAX_VALUE : left.getSortOrder();
                Integer rightOrder = right.getSortOrder() == null ? Integer.MAX_VALUE : right.getSortOrder();
                return leftOrder.compareTo(rightOrder);
            }
        });
        return responses;
    }

    @Override
    @Transactional
    public ClassroomSessionResponse enterNode(Long sessionId, Long nodeId) {
        User student = getCurrentStudent();
        ClassroomSession session = validateUnlockedNode(student, sessionId, nodeId);
        StudentProgress progress = getOrCreateProgress(session.getId(), student.getId(), nodeId);
        progress.setProgressStatus("doing");
        progress.setProgress(50);
        progress.setLastActiveAt(LocalDateTime.now());
        studentProgressRepository.save(progress);

        learningEventService.recordNodeEvent(sessionId, student.getId(), nodeId, "node_enter", Collections.<String, Object>emptyMap());
        return buildResponse(session);
    }

    @Override
    @Transactional
    public ClassroomSessionResponse submitNode(Long sessionId, Long nodeId, StudentNodeSubmitRequest request) {
        User student = getCurrentStudent();
        ClassroomSession session = validateUnlockedNode(student, sessionId, nodeId);
        ActivityNode node = activityNodeRepository.findById(nodeId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "activity node not found"));
        Map<String, Object> submittedResult = request.getResultJson() == null
                ? new HashMap<String, Object>()
                : new HashMap<String, Object>(request.getResultJson());
        Map<String, Object> assessmentResult = assessSubmission(node, submittedResult);
        Integer evaluatedScore = assessmentResult.get("score") instanceof Number
                ? ((Number) assessmentResult.get("score")).intValue()
                : null;
        submittedResult.put("_assessment", assessmentResult);
        Map<String, Object> eventData = new HashMap<>();
        eventData.put("resultType", request.getResultType());
        eventData.put("score", evaluatedScore);
        eventData.put("assessment", assessmentResult);
        eventData.put("wrongCount", safeInt(request.getWrongCount()));
        eventData.put("hintUsedCount", safeInt(request.getHintUsedCount()));
        eventData.put("durationSeconds", safeInt(request.getDurationSeconds()));
        eventData.put("resultJson", submittedResult);
        learningEventService.recordNodeEvent(sessionId, student.getId(), nodeId, "node_submit", eventData);

        StudentProgress progress = getOrCreateProgress(session.getId(), student.getId(), nodeId);
        progress.setProgressStatus("completed");
        progress.setProgress(100);
        progress.setScore(evaluatedScore);
        progress.setWrongCount(safeInt(request.getWrongCount()));
        progress.setHintUsedCount(safeInt(request.getHintUsedCount()));
        progress.setDurationSeconds(safeInt(request.getDurationSeconds()));
        progress.setResultJson(toJson(submittedResult));
        progress.setLastActiveAt(LocalDateTime.now());
        studentProgressRepository.save(progress);
        return buildResponse(session);
    }

    private Map<String, Object> assessSubmission(ActivityNode node, Map<String, Object> result) {
        Map<String, Object> runtime = extractActivityRuntime(node.getConfigJson());
        String renderer = String.valueOf(runtime.get("renderer") == null ? "completion" : runtime.get("renderer"));
        Map<String, Object> props = asMap(runtime.get("props"));
        Map<String, Object> assessment = asMap(runtime.get("assessment"));
        if (assessment.isEmpty()) {
            assessment = legacyAssessment(renderer);
        }

        PythonActivityAssessmentRequest request = new PythonActivityAssessmentRequest();
        request.setActivityId(String.valueOf(props.get("activityId") == null ? "" : props.get("activityId")));
        request.setRenderer(renderer);
        request.setTitle(node.getTitle());
        request.setResult(result);
        request.setAssessment(assessment);
        try {
            PythonCapabilityAssessmentResponse response = pythonCapabilityClient.assessActivity(request);
            JsonNode data = response == null ? null : response.getData();
            if (data == null || !data.isObject()) {
                return assessmentFallback(renderer, "Python assessment returned no data");
            }
            return objectMapper.convertValue(data, new TypeReference<Map<String, Object>>() {});
        } catch (RuntimeException exception) {
            return assessmentFallback(renderer, exception.getMessage());
        }
    }

    private Map<String, Object> extractActivityRuntime(String configJson) {
        if (configJson == null || configJson.trim().isEmpty()) {
            return Collections.emptyMap();
        }
        try {
            Map<String, Object> config = objectMapper.readValue(configJson, new TypeReference<Map<String, Object>>() {});
            return asMap(config.get("activityRuntime"));
        } catch (Exception ignored) {
            return Collections.emptyMap();
        }
    }

    private Map<String, Object> legacyAssessment(String renderer) {
        Map<String, Object> assessment = new HashMap<>();
        if (Arrays.asList("creation-panel", "virtual-instrument", "ensemble-roles").contains(renderer)) {
            assessment.put("mode", "ai");
        } else if (Arrays.asList("rhythm-drag", "solfege-sort", "melody-trace", "timbre-match", "form-order", "listening-choice", "singing-practice").contains(renderer)) {
            assessment.put("mode", "rule");
        } else {
            assessment.put("mode", "completion");
            assessment.put("scoreOnComplete", "summary".equals(renderer) ? null : 80);
        }
        return assessment;
    }

    private Map<String, Object> assessmentFallback(String renderer, String reason) {
        Map<String, Object> result = new HashMap<>();
        result.put("score", "summary".equals(renderer) ? null : 70);
        result.put("mode", "service_fallback");
        result.put("provider", "java");
        result.put("feedback", "评分服务暂不可用，已按任务完成度临时记录。");
        result.put("fallbackReason", reason == null ? "unknown" : reason);
        return result;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> asMap(Object value) {
        return value instanceof Map ? (Map<String, Object>) value : Collections.<String, Object>emptyMap();
    }

    private ClassroomSession validateUnlockedNode(User student, Long sessionId, Long nodeId) {
        ClassroomSession session = classroomSessionRepository.findById(sessionId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session not found"));
        if (!classMemberRepository.existsByClassIdAndUserIdAndStatus(session.getClassId(), student.getId(), "active")) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "student is not in this class");
        }
        if (!"running".equals(session.getStatus())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "classroom is not running");
        }

        PackagePublication publication = packagePublicationRepository.findById(session.getPublicationId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "publication not found"));
        if (!"published".equals(publication.getStatus())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package is not published");
        }
        if (!publication.getClassId().equals(session.getClassId()) || !publication.getPackageId().equals(session.getPackageId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "publication does not match session");
        }
        PackageVersion version = packageVersionRepository.findByIdAndPackageId(publication.getVersionId(), publication.getPackageId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package version not found"));
        if (!version.getPackageId().equals(session.getPackageId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "node package version mismatch");
        }

        ActivityNode node = activityNodeRepository.findById(nodeId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "activity node not found"));
        if (!session.getPackageId().equals(node.getPackageId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "node does not belong to this package");
        }
        SessionNodeState nodeState = sessionNodeStateRepository.findBySessionIdAndActivityNodeId(sessionId, nodeId)
                .orElseThrow(() -> new BusinessException(ErrorCode.ACTIVITY_LOCKED, ErrorCode.ACTIVITY_LOCKED.message()));
        if (!"unlocked".equals(nodeState.getStatus())) {
            throw new BusinessException(ErrorCode.ACTIVITY_LOCKED, ErrorCode.ACTIVITY_LOCKED.message());
        }
        return session;
    }

    private boolean isPublicationActive(ClassroomSession session) {
        if (session.getPublicationId() == null) {
            return false;
        }
        return packagePublicationRepository.findById(session.getPublicationId())
                .map(publication -> "published".equals(publication.getStatus()))
                .orElse(false);
    }

    private StudentProgress getOrCreateProgress(Long sessionId, Long studentId, Long nodeId) {
        return studentProgressRepository.findBySessionIdAndStudentIdAndCurrentNodeId(sessionId, studentId, nodeId)
                .orElseGet(() -> {
                    StudentProgress progress = new StudentProgress();
                    progress.setSessionId(sessionId);
                    progress.setStudentId(studentId);
                    progress.setCurrentNodeId(nodeId);
                    progress.setProgressStatus("not_started");
                    progress.setProgress(0);
                    return progress;
                });
    }

    private ClassroomSessionResponse buildResponse(ClassroomSession session) {
        List<SessionNodeState> states = sessionNodeStateRepository.findBySessionId(session.getId());
        List<Long> nodeIds = new ArrayList<>();
        for (SessionNodeState state : states) {
            nodeIds.add(state.getActivityNodeId());
        }

        Map<Long, ActivityNode> nodesById = new HashMap<>();
        if (!nodeIds.isEmpty()) {
            for (ActivityNode node : activityNodeRepository.findByIdIn(nodeIds)) {
                nodesById.put(node.getId(), node);
            }
        }

        List<SessionNodeStateResponse> stateResponses = new ArrayList<>();
        for (SessionNodeState state : states) {
            stateResponses.add(SessionNodeStateResponse.from(state, nodesById.get(state.getActivityNodeId())));
        }
        Collections.sort(stateResponses, new Comparator<SessionNodeStateResponse>() {
            @Override
            public int compare(SessionNodeStateResponse left, SessionNodeStateResponse right) {
                Integer leftOrder = left.getSortOrder() == null ? Integer.MAX_VALUE : left.getSortOrder();
                Integer rightOrder = right.getSortOrder() == null ? Integer.MAX_VALUE : right.getSortOrder();
                return leftOrder.compareTo(rightOrder);
            }
        });
        return ClassroomSessionResponse.from(session, stateResponses);
    }

    private User getCurrentStudent() {
        User user = userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "login user not found"));
        if (user.getRole() != UserRole.student) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "student permission required");
        }
        return user;
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
    }

    private int safeInt(Integer value) {
        return value == null ? 0 : value;
    }

    private String toJson(Object value) {
        if (value == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(value);
        } catch (JsonProcessingException exception) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "result json is not valid");
        }
    }
}

