package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.PublishPackageRequest;
import com.buyilehu.musicagent.application.dto.response.PackagePublicationResponse;

public interface PackagePublicationService {
    PackagePublicationResponse publish(Long packageId, PublishPackageRequest request);
}
