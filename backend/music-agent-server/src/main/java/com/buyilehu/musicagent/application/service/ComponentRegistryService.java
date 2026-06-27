package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.domain.entity.ComponentDefinition;

public interface ComponentRegistryService {
    ComponentDefinition getOrCreate(String componentKey);
}
