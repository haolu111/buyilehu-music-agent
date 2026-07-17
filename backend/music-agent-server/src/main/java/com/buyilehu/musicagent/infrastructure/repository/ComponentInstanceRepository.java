package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ComponentInstance;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ComponentInstanceRepository extends JpaRepository<ComponentInstance, Long> {
    List<ComponentInstance> findByActivityNodeIdIn(List<Long> activityNodeIds);

    List<ComponentInstance> findByActivityNodeIdOrderBySortOrderAsc(Long activityNodeId);
}