package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.generator.QualityReportGenerator;
import com.buyilehu.musicagent.application.service.MusicValidationService;
import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityNodeConfig;
import com.buyilehu.musicagent.domain.model.QualityCheckResult;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class MusicValidationServiceImpl implements MusicValidationService {
    private final QualityReportGenerator qualityReportGenerator;

    public MusicValidationServiceImpl(QualityReportGenerator qualityReportGenerator) {
        this.qualityReportGenerator = qualityReportGenerator;
    }

    @Override
    public QualityCheckResult validate(ActivityChain chain, List<ActivityNodeConfig> nodeConfigs) {
        return qualityReportGenerator.check(chain, nodeConfigs);
    }
}
