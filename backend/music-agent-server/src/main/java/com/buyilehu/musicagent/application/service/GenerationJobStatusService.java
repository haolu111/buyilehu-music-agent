package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.GenerationJobResponse;
import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.domain.entity.GenerationJob;
import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import com.buyilehu.musicagent.domain.entity.PackageVersion;
import com.buyilehu.musicagent.infrastructure.repository.InteractivePackageRepository;
import com.buyilehu.musicagent.infrastructure.repository.PackageVersionRepository;
import com.buyilehu.musicagent.infrastructure.status.GenerationJobStatusStore;
import java.time.LocalDateTime;
import org.springframework.stereotype.Service;

@Service
public class GenerationJobStatusService {
    private final GenerationJobStatusStore statusStore;
    private final InteractivePackageRepository packageRepository;
    private final PackageVersionRepository packageVersionRepository;

    public GenerationJobStatusService(GenerationJobStatusStore statusStore,
                                      InteractivePackageRepository packageRepository,
                                      PackageVersionRepository packageVersionRepository) {
        this.statusStore = statusStore;
        this.packageRepository = packageRepository;
        this.packageVersionRepository = packageVersionRepository;
    }

    public GenerationJobStatus queued(GenerationJob job) {
        return publish(job, "queued", "queued", 0, "任务已进入生成队列");
    }

    public GenerationJobStatus progress(GenerationJob job, String phase, int progress, String message) {
        return publish(job, "running", phase, progress, message);
    }

    public GenerationJobStatus completed(GenerationJobResponse response) {
        GenerationJobStatus status = new GenerationJobStatus();
        copyResponse(response, status);
        status.setStatus("success");
        status.setPhase("completed");
        status.setProgress(100);
        status.setMessage("互动包生成完成");
        status.setUpdatedAt(LocalDateTime.now());
        statusStore.save(status);
        return status;
    }

    public GenerationJobStatus failed(GenerationJob job) {
        GenerationJobStatus status = fromDatabase(job);
        status.setStatus("failed");
        status.setPhase("failed");
        status.setProgress(100);
        status.setMessage("互动包生成失败");
        status.setErrorMessage(job.getErrorMessage());
        status.setUpdatedAt(LocalDateTime.now());
        statusStore.save(status);
        return status;
    }

    public GenerationJobStatus find(GenerationJob job) {
        return statusStore.find(job.getId()).orElseGet(() -> fromDatabase(job));
    }

    private GenerationJobStatus publish(GenerationJob job, String state, String phase,
                                        int progress, String message) {
        GenerationJobStatus status = fromDatabase(job);
        status.setStatus(state);
        status.setPhase(phase);
        status.setProgress(progress);
        status.setMessage(message);
        status.setUpdatedAt(LocalDateTime.now());
        statusStore.save(status);
        return status;
    }

    private GenerationJobStatus fromDatabase(GenerationJob job) {
        GenerationJobStatus status = new GenerationJobStatus();
        status.setId(job.getId());
        status.setLessonPlanId(job.getLessonPlanId());
        status.setStatus(job.getStatus());
        status.setProgress(job.getProgress());
        status.setErrorMessage(job.getErrorMessage());
        status.setUpdatedAt(job.getUpdatedAt());
        packageRepository.findFirstByGenerationJobId(job.getId()).ifPresent(pkg -> {
            status.setPackageId(pkg.getId());
            packageVersionRepository.findFirstByPackageIdOrderByVersionNoDesc(pkg.getId())
                    .map(PackageVersion::getId)
                    .ifPresent(status::setVersionId);
        });
        return status;
    }

    private void copyResponse(GenerationJobResponse response, GenerationJobStatus status) {
        status.setId(response.getId());
        status.setLessonPlanId(response.getLessonPlanId());
        status.setPackageId(response.getPackageId());
        status.setVersionId(response.getVersionId());
        status.setErrorMessage(response.getErrorMessage());
        status.setDesignProvider(response.getDesignProvider());
        status.setDesignModel(response.getDesignModel());
        status.setDesignFallbackReason(response.getDesignFallbackReason());
        status.setDesignTraceId(response.getDesignTraceId());
    }
}
