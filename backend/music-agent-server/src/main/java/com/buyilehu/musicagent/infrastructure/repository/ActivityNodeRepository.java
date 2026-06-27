package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ActivityNodeRepository extends JpaRepository<ActivityNode, Long> {
    List<ActivityNode> findByPackageIdOrderBySortOrderAsc(Long packageId);

    List<ActivityNode> findByIdIn(List<Long> ids);

    Optional<ActivityNode> findByIdAndPackageId(Long id, Long packageId);
}