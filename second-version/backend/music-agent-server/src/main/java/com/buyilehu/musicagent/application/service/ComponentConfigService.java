package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.domain.entity.ActivityNode;

public interface ComponentConfigService {
    void applyComponentConfig(ActivityNode node, PackageNodeConfigUpdateRequest request);
}