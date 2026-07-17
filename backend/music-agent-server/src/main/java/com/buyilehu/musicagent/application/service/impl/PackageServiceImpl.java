package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.response.PackageResponse;
import com.buyilehu.musicagent.application.service.PackageService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.LessonPlan;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.util.ArrayList;
import java.util.List;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
public class PackageServiceImpl implements PackageService {
    private final InteractivePackageRepository interactivePackageRepository;
    private final UserRepository userRepository;

    public PackageServiceImpl(InteractivePackageRepository interactivePackageRepository,
                              UserRepository userRepository) {
        this.interactivePackageRepository = interactivePackageRepository;
        this.userRepository = userRepository;
    }

    @Override
    public InteractivePackage createPackage(LessonPlan lessonPlan, ParsedLesson parsedLesson, Long generationJobId) {
        InteractivePackage pkg = new InteractivePackage();
        pkg.setLessonPlanId(lessonPlan.getId());
        pkg.setGenerationJobId(generationJobId);
        pkg.setOwnerId(lessonPlan.getTeacherId());
        pkg.setTitle(parsedLesson.getCourseName() + "互动包");
        pkg.setDescription("基于教案《" + lessonPlan.getTitle() + "》生成的标准五段式互动课堂包");
        pkg.setStatus("generated");
        return interactivePackageRepository.save(pkg);
    }

    @Override
    public PackageResponse getPackage(Long packageId) {
        return PackageResponse.from(getOwnedPackage(packageId));
    }

    @Override
    public List<PackageResponse> listMyPackages() {
        User currentUser = getCurrentTeacher();
        List<InteractivePackage> packages = interactivePackageRepository.findByOwnerIdOrderByIdDesc(currentUser.getId());
        List<PackageResponse> responses = new ArrayList<>();
        for (InteractivePackage pkg : packages) {
            responses.add(PackageResponse.from(pkg));
        }
        return responses;
    }

    private InteractivePackage getOwnedPackage(Long packageId) {
        User currentUser = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package not found"));
        if (!currentUser.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package access denied");
        }
        return pkg;
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
