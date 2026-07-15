package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import java.util.List;

public interface MusicValidationService {
    QualityCheckResult validate(ActivityChain chain, List<ActivityNodeConfig> nodeConfigs);
}
