package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.PublishPackageRequest;
import com.buyilehu.musicagent.application.dto.response.PackagePublicationResponse;
import com.buyilehu.musicagent.application.service.PackagePublicationService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ClassEntity;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.PackagePublication;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ClassRepository;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackagePublicationRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.time.LocalDateTime;
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
    private final UserRepository userRepository;

    public PackagePublicationServiceImpl(PackagePublicationRepository packagePublicationRepository,
                                         InteractivePackageRepository interactivePackageRepository,
                                         PackageVersionRepository packageVersionRepository,
                                         ClassRepository classRepository,
                                         UserRepository userRepository) {
        this.packagePublicationRepository = packagePublicationRepository;
        this.interactivePackageRepository = interactivePackageRepository;
        this.packageVersionRepository = packageVersionRepository;
        this.classRepository = classRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public PackagePublicationResponse publish(Long packageId, PublishPackageRequest request) {
        User teacher = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "互动包不存在"));
        if (!teacher.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能发布自己的互动包");
        }

        Long versionId = request.getVersionId() != null ? request.getVersionId() : pkg.getCurrentVersionId();
        if (versionId == null) {
            throw new BusinessException(ErrorCode.PARAM_ERROR, "请先选择要发布的版本");
        }

        PackageVersion version = packageVersionRepository.findByIdAndPackageId(versionId, packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "版本不存在或不属于该互动包"));
        ClassEntity classEntity = classRepository.findById(request.getClassId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "班级不存在"));
        if (!teacher.getId().equals(classEntity.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能发布到自己创建的班级");
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
        log.info("Package published: publicationId={}, packageId={}, versionId={}, classId={}, teacherId={}",
                savedPublication.getId(), packageId, versionId, classEntity.getId(), teacher.getId());
        return PackagePublicationResponse.from(savedPublication);
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
