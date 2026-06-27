package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.response.PackageVersionResponse;
import com.buyilehu.musicagent.application.service.PackageVersionService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.util.ArrayList;
import java.util.List;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
public class PackageVersionServiceImpl implements PackageVersionService {
    private final PackageVersionRepository packageVersionRepository;
    private final InteractivePackageRepository interactivePackageRepository;
    private final UserRepository userRepository;

    public PackageVersionServiceImpl(PackageVersionRepository packageVersionRepository,
                                     InteractivePackageRepository interactivePackageRepository,
                                     UserRepository userRepository) {
        this.packageVersionRepository = packageVersionRepository;
        this.interactivePackageRepository = interactivePackageRepository;
        this.userRepository = userRepository;
    }

    @Override
    public PackageVersion getLatestVersion(Long packageId) {
        return packageVersionRepository.findFirstByPackageIdOrderByVersionNoDesc(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package version not found"));
    }

    @Override
    public PackageVersion confirmLatestVersion(Long packageId) {
        PackageVersion version = getLatestVersion(packageId);
        version.setStatus("confirmed");
        return packageVersionRepository.save(version);
    }

    @Override
    public List<PackageVersionResponse> listVersions(Long packageId) {
        assertPackageOwner(packageId);
        List<PackageVersionResponse> responses = new ArrayList<>();
        for (PackageVersion version : packageVersionRepository.findByPackageIdOrderByVersionNoDesc(packageId)) {
            responses.add(PackageVersionResponse.from(version));
        }
        return responses;
    }

    private void assertPackageOwner(Long packageId) {
        User user = getCurrentTeacher();
        InteractivePackage pkg = interactivePackageRepository.findById(packageId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "package not found"));
        if (!user.getId().equals(pkg.getOwnerId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "package access denied");
        }
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