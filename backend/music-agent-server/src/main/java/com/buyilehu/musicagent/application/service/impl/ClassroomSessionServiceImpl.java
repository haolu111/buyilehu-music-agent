package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.CreateClassroomSessionRequest;
import com.buyilehu.musicagent.application.dto.response.ClassroomSessionResponse;
import com.buyilehu.musicagent.application.dto.response.SessionNodeStateResponse;
import com.buyilehu.musicagent.application.service.ClassroomSessionService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import com.buyilehu.musicagent.domain.entity.PackagePublication;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassMemberRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassroomSessionRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackagePublicationRepository;
import com.buyilehu.musicagent.infrastructure.repository.SessionNodeStateRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.time.LocalDateTime;
import java.util.ArrayList;
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
public class ClassroomSessionServiceImpl implements ClassroomSessionService {
    private final ClassroomSessionRepository classroomSessionRepository;
    private final PackagePublicationRepository packagePublicationRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final SessionNodeStateRepository sessionNodeStateRepository;
    private final ClassMemberRepository classMemberRepository;
    private final UserRepository userRepository;

    public ClassroomSessionServiceImpl(ClassroomSessionRepository classroomSessionRepository,
                                       PackagePublicationRepository packagePublicationRepository,
                                       ActivityNodeRepository activityNodeRepository,
                                       SessionNodeStateRepository sessionNodeStateRepository,
                                       ClassMemberRepository classMemberRepository,
                                       UserRepository userRepository) {
        this.classroomSessionRepository = classroomSessionRepository;
        this.packagePublicationRepository = packagePublicationRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.sessionNodeStateRepository = sessionNodeStateRepository;
        this.classMemberRepository = classMemberRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public ClassroomSessionResponse create(CreateClassroomSessionRequest request) {
        User teacher = getCurrentTeacher();
        PackagePublication publication = packagePublicationRepository
                .findByIdAndPublishedBy(request.getPublicationId(), teacher.getId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "publication not found"));
        if (!"published".equals(publication.getStatus())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "publication is not published");
        }

        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(publication.getPackageId());
        if (nodes.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "activity nodes not found");
        }

        ClassroomSession session = new ClassroomSession();
        session.setPublicationId(publication.getId());
        session.setClassId(publication.getClassId());
        session.setPackageId(publication.getPackageId());
        session.setTeacherId(teacher.getId());
        session.setStatus("not_started");
        ClassroomSession savedSession = classroomSessionRepository.save(session);

        List<SessionNodeState> states = new ArrayList<>();
        for (ActivityNode node : nodes) {
            SessionNodeState state = new SessionNodeState();
            state.setSessionId(savedSession.getId());
            state.setActivityNodeId(node.getId());
            state.setStatus("locked");
            states.add(state);
        }
        sessionNodeStateRepository.saveAll(states);
        return buildResponse(savedSession);
    }

    @Override
    @Transactional(readOnly = true)
    public ClassroomSessionResponse get(Long sessionId) {
        User user = getCurrentUser();
        ClassroomSession session = classroomSessionRepository.findById(sessionId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session not found"));
        assertSessionReadable(session, user);
        return buildResponse(session);
    }

    @Override
    @Transactional
    public ClassroomSessionResponse start(Long sessionId) {
        ClassroomSession session = getTeacherSession(sessionId);
        if ("ended".equals(session.getStatus())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "session already ended");
        }
        session.setStatus("running");
        if (session.getStartedAt() == null) {
            session.setStartedAt(LocalDateTime.now());
        }
        return buildResponse(classroomSessionRepository.save(session));
    }

    @Override
    @Transactional
    public ClassroomSessionResponse unlockNode(Long sessionId, Long nodeId) {
        ClassroomSession session = getTeacherSession(sessionId);
        if (!"running".equals(session.getStatus())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "session is not running");
        }
        SessionNodeState nodeState = sessionNodeStateRepository.findBySessionIdAndActivityNodeId(sessionId, nodeId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session node state not found"));
        nodeState.setStatus("unlocked");
        nodeState.setUnlockedAt(LocalDateTime.now());
        sessionNodeStateRepository.save(nodeState);

        session.setCurrentNodeId(nodeId);
        return buildResponse(classroomSessionRepository.save(session));
    }

    @Override
    @Transactional
    public ClassroomSessionResponse pause(Long sessionId) {
        ClassroomSession session = getTeacherSession(sessionId);
        if (!"running".equals(session.getStatus())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "only running session can be paused");
        }
        session.setStatus("paused");
        return buildResponse(classroomSessionRepository.save(session));
    }

    @Override
    @Transactional
    public ClassroomSessionResponse end(Long sessionId) {
        ClassroomSession session = getTeacherSession(sessionId);
        if (!"ended".equals(session.getStatus())) {
            session.setStatus("ended");
            session.setEndedAt(LocalDateTime.now());
        }
        return buildResponse(classroomSessionRepository.save(session));
    }

    private ClassroomSession getTeacherSession(Long sessionId) {
        User teacher = getCurrentTeacher();
        return classroomSessionRepository.findByIdAndTeacherId(sessionId, teacher.getId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session not found"));
    }

    private void assertSessionReadable(ClassroomSession session, User user) {
        if (user.getRole() == UserRole.teacher && user.getId().equals(session.getTeacherId())) {
            return;
        }
        if (user.getRole() == UserRole.student
                && classMemberRepository.existsByClassIdAndUserId(session.getClassId(), user.getId())) {
            return;
        }
        throw new BusinessException(ErrorCode.FORBIDDEN, "session access denied");
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

    private User getCurrentTeacher() {
        User user = getCurrentUser();
        if (user.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "teacher permission required");
        }
        return user;
    }

    private User getCurrentUser() {
        return userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "login user not found"));
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
}
