package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.PublishPackageRequest;
import com.buyilehu.musicagent.application.dto.response.PackageResponse;
import com.buyilehu.musicagent.application.dto.response.PackagePublicationResponse;
import com.buyilehu.musicagent.application.dto.response.ProposalCardResponse;
import com.buyilehu.musicagent.application.service.PackagePublicationService;
import com.buyilehu.musicagent.application.service.PackageService;
import com.buyilehu.musicagent.application.service.ProposalCardService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import java.util.List;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/packages")
public class PackageController {
    private final PackageService packageService;
    private final ProposalCardService proposalCardService;
    private final PackagePublicationService packagePublicationService;

    public PackageController(PackageService packageService,
                             ProposalCardService proposalCardService,
                             PackagePublicationService packagePublicationService) {
        this.packageService = packageService;
        this.proposalCardService = proposalCardService;
        this.packagePublicationService = packagePublicationService;
    }

    @GetMapping("/{packageId}/proposal")
    public ApiResponse<ProposalCardResponse> getProposal(@PathVariable Long packageId) {
        return ApiResponse.success(proposalCardService.getProposal(packageId));
    }

    @PostMapping("/{packageId}/proposal/confirm")
    public ApiResponse<ProposalCardResponse> confirmProposal(@PathVariable Long packageId) {
        return ApiResponse.success(proposalCardService.confirmProposal(packageId));
    }

    @GetMapping("/{packageId}")
    public ApiResponse<PackageResponse> getPackage(@PathVariable Long packageId) {
        return ApiResponse.success(packageService.getPackage(packageId));
    }

    @GetMapping
    public ApiResponse<List<PackageResponse>> listPackages() {
        return ApiResponse.success(packageService.listMyPackages());
    }

    @PostMapping("/{packageId}/publish")
    public ApiResponse<PackagePublicationResponse> publish(@PathVariable Long packageId,
                                                           @Valid @RequestBody PublishPackageRequest request) {
        return ApiResponse.success(packagePublicationService.publish(packageId, request));
    }
}
