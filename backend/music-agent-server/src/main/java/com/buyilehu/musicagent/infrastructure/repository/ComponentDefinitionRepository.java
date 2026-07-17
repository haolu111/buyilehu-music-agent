package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ComponentDefinition;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ComponentDefinitionRepository extends JpaRepository<ComponentDefinition, Long> {
    Optional<ComponentDefinition> findByComponentKey(String componentKey);
}
