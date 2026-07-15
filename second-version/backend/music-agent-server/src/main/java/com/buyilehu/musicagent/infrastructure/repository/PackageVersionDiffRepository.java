package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.PackageVersionDiff;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PackageVersionDiffRepository extends JpaRepository<PackageVersionDiff, Long> {
    List<PackageVersionDiff> findByPackageIdOrderByIdDesc(Long packageId);
}