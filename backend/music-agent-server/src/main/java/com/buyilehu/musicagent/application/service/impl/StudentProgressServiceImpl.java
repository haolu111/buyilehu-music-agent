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
import com.fasterxml.jackson.core.JsonProcessingException;
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

    public StudentProgressServiceImpl(ClassroomSessionRepository classroomSessionRepository,
                                      PackagePublicationRepository packagePublicationRepository,
                                      PackageVersionRepository packageVersionRepository,
                                      SessionNodeStateRepository sessionNodeStateRepository,
                                      ActivityNodeRepository activityNodeRepository,
                                      ClassMemberRepository classMemberRepository,
                                      StudentProgressRepository studentProgressRepository,
                                      UserRepository userRepository,
                                      LearningEventService learningEventService,
                                      ObjectMapper objectMapper) {
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
        Map<String, Object> eventData = new HashMap<>();
        eventData.put("resultType", request.getResultType());
        eventData.put("score", request.getScore());
        eventData.put("wrongCount", safeInt(request.getWrongCount()));
        eventData.put("hintUsedCount", safeInt(request.getHintUsedCount()));
        eventData.put("durationSeconds", safeInt(request.getDurationSeconds()));
        eventData.put("resultJson", request.getResultJson());
        learningEventService.recordNodeEvent(sessionId, student.getId(), nodeId, "node_submit", eventData);

        StudentProgress progress = getOrCreateProgress(session.getId(), student.getId(), nodeId);
        progress.setProgressStatus("completed");
        progress.setProgress(100);
        progress.setScore(request.getScore());
        progress.setWrongCount(safeInt(request.getWrongCount()));
        progress.setHintUsedCount(safeInt(request.getHintUsedCount()));
        progress.setDurationSeconds(safeInt(request.getDurationSeconds()));
        progress.setResultJson(toJson(request.getResultJson()));
        progress.setLastActiveAt(LocalDateTime.now());
        studentProgressRepository.save(progress);
        return buildResponse(session);
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

