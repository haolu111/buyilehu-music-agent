package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.QualityReport;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface QualityReportRepository extends JpaRepository<QualityReport, Long> {
    List<QualityReport> findByPackageId(Long packageId);
}
