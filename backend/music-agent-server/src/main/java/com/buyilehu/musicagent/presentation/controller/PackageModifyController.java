package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.PackageModifyRequest;
import com.buyilehu.musicagent.application.dto.request.PackageNodeConfigUpdateRequest;
import com.buyilehu.musicagent.application.dto.response.PackageModifyResponse;
import com.buyilehu.musicagent.application.dto.response.PackageVersionResponse;
import com.buyilehu.musicagent.application.service.PackageModifyService;
import com.buyilehu.musicagent.application.service.PackageVersionService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/packages")
public class PackageModifyController {
    private final PackageModifyService packageModifyService;
    private final PackageVersionService packageVersionService;

    public PackageModifyController(PackageModifyService packageModifyService,
                                   PackageVersionService packageVersionService) {
        this.packageModifyService = packageModifyService;
        this.packageVersionService = packageVersionService;
    }

    @PatchMapping("/{packageId}/nodes/{nodeId}/config")
    public ApiResponse<PackageModifyResponse> updateNodeConfig(@PathVariable @Positive Long packageId,
                                                               @PathVariable @Positive Long nodeId,
                                                               @Valid @RequestBody PackageNodeConfigUpdateRequest request) {
        return ApiResponse.success(packageModifyService.updateNodeConfig(packageId, nodeId, request));
    }

    @PostMapping("/{packageId}/modify")
    public ApiResponse<PackageModifyResponse> modify(@PathVariable @Positive Long packageId,
                                                     @Valid @RequestBody PackageModifyRequest request) {
        return ApiResponse.success(packageModifyService.modify(packageId, request));
    }

    @GetMapping("/{packageId}/versions")
    public ApiResponse<List<PackageVersionResponse>> listVersions(@PathVariable @Positive Long packageId) {
        return ApiResponse.success(packageVersionService.listVersions(packageId));
    }
}