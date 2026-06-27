package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.service.ComponentRegistryService;
import com.buyilehu.musicagent.domain.entity.ComponentDefinition;
import com.buyilehu.musicagent.infrastructure.repository.ComponentDefinitionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ComponentRegistryServiceImpl implements ComponentRegistryService {
    private final ComponentDefinitionRepository componentDefinitionRepository;

    public ComponentRegistryServiceImpl(ComponentDefinitionRepository componentDefinitionRepository) {
        this.componentDefinitionRepository = componentDefinitionRepository;
    }

    @Override
    @Transactional
    public ComponentDefinition getOrCreate(String componentKey) {
        return componentDefinitionRepository.findByComponentKey(componentKey)
                .orElseGet(() -> {
                    ComponentDefinition definition = new ComponentDefinition();
                    definition.setComponentKey(componentKey);
                    definition.setName(resolveName(componentKey));
                    definition.setCategory(resolveCategory(componentKey));
                    definition.setSchemaJson("{}");
                    definition.setStatus("active");
                    return componentDefinitionRepository.save(definition);
                });
    }

    private String resolveName(String componentKey) {
        return componentKey.replace('_', ' ');
    }

    private String resolveCategory(String componentKey) {
        if (componentKey.contains("beat") || componentKey.contains("meter")) {
            return "meter";
        }
        if (componentKey.contains("rhythm")) {
            return "rhythm";
        }
        if (componentKey.contains("creation")) {
            return "creation";
        }
        return "display";
    }
}
