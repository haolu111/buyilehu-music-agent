package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.PackageModifyRequest;
import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.application.dto.response.PackageModifyResponse;

public interface PackageModifyService {
    PackageModifyResponse updateNodeConfig(Long packageId, Long nodeId, PackageNodeConfigUpdateRequest request);

    PackageModifyResponse modify(Long packageId, PackageModifyRequest request);
}