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
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PackagePublicationServiceImpl implements PackagePublicationService {
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
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package not found"));
        if (!teacher.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package access denied");
        }

        PackageVersion version = packageVersionRepository.findByIdAndPackageId(request.getVersionId(), packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package version not found"));
        ClassEntity classEntity = classRepository.findById(request.getClassId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "class not found"));
        if (!teacher.getId().equals(classEntity.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "class access denied");
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
        return PackagePublicationResponse.from(packagePublicationRepository.save(publication));
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
