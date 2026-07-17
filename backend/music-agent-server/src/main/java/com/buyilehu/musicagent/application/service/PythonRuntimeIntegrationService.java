package com.buyilehu.musicagent.application.service;

import java.util.List;

import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;

public interface PythonRuntimeIntegrationService {
    void enrichNodes(ParsedLesson parsedLesson, GeneratePreferences preferences, List<ActivityNodeConfig> nodeConfigs);
}
