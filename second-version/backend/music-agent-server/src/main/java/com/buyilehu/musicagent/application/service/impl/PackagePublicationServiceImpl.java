package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.PublishPackageRequest;
import com.buyilehu.musicagent.application.dto.response.PackagePublicationResponse;
import com.buyilehu.musicagent.application.service.PackagePublicationService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ClassEntity;
import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.PackagePublication;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassroomSessionRepository;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackagePublicationRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.SessionNodeStateRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PackagePublicationServiceImpl implements PackagePublicationService {
    private static final Logger log = LoggerFactory.getLogger(PackagePublicationServiceImpl.class);
    private final PackagePublicationRepository packagePublicationRepository;
    private final InteractivePackageRepository interactivePackageRepository;
    private final PackageVersionRepository packageVersionRepository;
    private final ClassRepository classRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final ClassroomSessionRepository classroomSessionRepository;
    private final SessionNodeStateRepository sessionNodeStateRepository;
    private final UserRepository userRepository;

    public PackagePublicationServiceImpl(PackagePublicationRepository packagePublicationRepository,
                                         InteractivePackageRepository interactivePackageRepository,
                                         PackageVersionRepository packageVersionRepository,
                                         ClassRepository classRepository,
                                         ActivityNodeRepository activityNodeRepository,
                                         ClassroomSessionRepository classroomSessionRepository,
                                         SessionNodeStateRepository sessionNodeStateRepository,
                                         UserRepository userRepository) {
        this.packagePublicationRepository = packagePublicationRepository;
        this.interactivePackageRepository = interactivePackageRepository;
        this.packageVersionRepository = packageVersionRepository;
        this.classRepository = classRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.classroomSessionRepository = classroomSessionRepository;
        this.sessionNodeStateRepository = sessionNodeStateRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public PackagePublicationResponse publish(Long packageId, PublishPackageRequest request) {
        User teacher = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "interactive package not found"));
        if (!teacher.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "only owner can publish package");
        }

        Long versionId = request.getVersionId() != null ? request.getVersionId() : pkg.getCurrentVersionId();
        if (versionId == null) {
            throw new BusinessException(ErrorCode.PARAM_ERROR, "package version is required");
        }
        PackageVersion version = packageVersionRepository.findByIdAndPackageId(versionId, packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package version not found"));

        List<Long> classIds = resolveClassIds(request);
        PackagePublication firstPublication = null;
        ClassroomSession firstSession = null;
        for (Long classId : classIds) {
            ClassEntity classEntity = classRepository.findById(classId)
                    .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "class not found"));
            if (!teacher.getId().equals(classEntity.getTeacherId())) {
                throw new BusinessException(ErrorCode.FORBIDDEN, "only class owner can publish to class");
            }

            PackagePublication publication = new PackagePublication();
            publication.setPackageId(pkg.getId());
            publication.setVersionId(version.getId());
            publication.setClassId(classEntity.getId());
            publication.setPublishedBy(teacher.getId());
            publication.setPublishChannel("classroom");
            publication.setStatus("published");
            publication.setReviewEnabled(Boolean.TRUE.equals(request.getReviewEnabled()));
            publication.setPublishedAt(LocalDateTime.now());
            PackagePublication savedPublication = packagePublicationRepository.save(publication);

            ClassroomSession session = createSession(savedPublication, teacher.getId(), request);
            if (firstPublication == null) {
                firstPublication = savedPublication;
                firstSession = session;
            }
            log.info("Package published to class: publicationId={}, sessionId={}, packageId={}, versionId={}, classId={}, teacherId={}",
                    savedPublication.getId(), session.getId(), packageId, versionId, classEntity.getId(), teacher.getId());
        }
        log.info("Package publish completed: packageId={}, classCount={}, firstSessionId={}",
                packageId, classIds.size(), firstSession == null ? null : firstSession.getId());
        return PackagePublicationResponse.from(firstPublication);
    }

    private List<Long> resolveClassIds(PublishPackageRequest request) {
        Set<Long> ids = new LinkedHashSet<>();
        if (request.getClassIds() != null) {
            ids.addAll(request.getClassIds());
        }
        if (request.getClassId() != null) {
            ids.add(request.getClassId());
        }
        if (ids.isEmpty()) {
            throw new BusinessException(ErrorCode.PARAM_ERROR, "class is required");
        }
        return new ArrayList<>(ids);
    }

    private ClassroomSession createSession(PackagePublication publication, Long teacherId, PublishPackageRequest request) {
        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(publication.getPackageId());
        if (nodes.isEmpty()) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "activity nodes not found");
        }

        boolean startImmediately = false;
        LocalDateTime now = LocalDateTime.now();
        ClassroomSession session = new ClassroomSession();
        session.setPublicationId(publication.getId());
        session.setClassId(publication.getClassId());
        session.setPackageId(publication.getPackageId());
        session.setTeacherId(teacherId);
        session.setCourseTitle(request.getCourseTitle());
        session.setCourseDescription(request.getCourseDescription());
        session.setScheduledStartAt(request.getScheduledStartAt());
        session.setStatus(startImmediately ? "running" : "not_started");
        if (startImmediately) {
            session.setStartedAt(now);
            session.setCurrentNodeId(nodes.get(0).getId());
        }
        ClassroomSession savedSession = classroomSessionRepository.save(session);

        List<SessionNodeState> states = new ArrayList<>();
        for (int index = 0; index < nodes.size(); index++) {
            ActivityNode node = nodes.get(index);
            SessionNodeState state = new SessionNodeState();
            state.setSessionId(savedSession.getId());
            state.setActivityNodeId(node.getId());
            if (startImmediately && index == 0) {
                state.setStatus("unlocked");
                state.setUnlockedAt(now);
            } else {
                state.setStatus("locked");
            }
            states.add(state);
        }
        sessionNodeStateRepository.saveAll(states);
        return savedSession;
    }

    private User getCurrentTeacher() {
        User user = userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "login user not found"));
        if (user.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "teacher permission required");
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
}
