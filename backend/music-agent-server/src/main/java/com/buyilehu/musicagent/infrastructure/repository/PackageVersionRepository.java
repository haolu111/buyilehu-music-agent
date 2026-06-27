package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.PackageVersion;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PackageVersionRepository extends JpaRepository<PackageVersion, Long> {
    Optional<PackageVersion> findFirstByPackageIdOrderByVersionNoDesc(Long packageId);

    Optional<PackageVersion> findByIdAndPackageId(Long id, Long packageId);

    List<PackageVersion> findByPackageIdOrderByVersionNoDesc(Long packageId);
}