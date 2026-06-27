package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.PackageModifyRecord;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PackageModifyRecordRepository extends JpaRepository<PackageModifyRecord, Long> {
    List<PackageModifyRecord> findByPackageIdOrderByIdDesc(Long packageId);
}