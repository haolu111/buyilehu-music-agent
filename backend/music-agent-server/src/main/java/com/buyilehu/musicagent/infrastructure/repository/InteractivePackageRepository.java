package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.InteractivePackage;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InteractivePackageRepository extends JpaRepository<InteractivePackage, Long> {
    List<InteractivePackage> findByOwnerIdOrderByIdDesc(Long ownerId);
}
