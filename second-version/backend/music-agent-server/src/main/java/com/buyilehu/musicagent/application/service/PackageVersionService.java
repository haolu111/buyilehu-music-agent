package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.PackageVersionResponse;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import java.util.List;

public interface PackageVersionService {
    PackageVersion getLatestVersion(Long packageId);

    PackageVersion confirmLatestVersion(Long packageId);

    List<PackageVersionResponse> listVersions(Long packageId);
}