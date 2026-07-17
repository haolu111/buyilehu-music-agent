package com.buyilehu.musicagent.application.generator;

import com.buyilehu.musicagent.domain.model.ActivityChain;
import com.buyilehu.musicagent.domain.model.ActivityStep;
import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import com.buyilehu.musicagent.domain.model.ParsedLesson;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityClient;
import com.buyilehu.musicagent.infrastructure.capability.PythonCapabilityProperties;
import com.buyilehu.musicagent.infrastructure.capability.PythonRuntimeRequestFactory;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonPackageDesignData;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonPackageDesignMetadata;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonPackageDesignResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonPackageDesignStep;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class LessonToPackageGenerator {
    private final ActivityChainGenerator activityChainGenerator;
    private final PythonCapabilityClient pythonCapabilityClient;
    private final PythonRuntimeRequestFactory requestFactory;
    private final PythonCapabilityProperties properties;

    public LessonToPackageGenerator(ActivityChainGenerator activityChainGenerator,
                                    PythonCapabilityClient pythonCapabilityClient,
                                    PythonRuntimeRequestFactory requestFactory,
                                    PythonCapabilityProperties properties) {
        this.activityChainGenerator = activityChainGenerator;
        this.pythonCapabilityClient = pythonCapabilityClient;
        this.requestFactory = requestFactory;
        this.properties = properties;
    }

    public ActivityChain generate(ParsedLesson parsedLesson, GeneratePreferences preferences) {
        if (!properties.isEnabled()) {
            return fallback(parsedLesson, preferences, "Python capability is disabled");
        }
        try {
            PythonPackageDesignResponse response = pythonCapabilityClient.designPackage(
                    requestFactory.buildDesign(parsedLesson, preferences));
            return toActivityChain(response);
        } catch (RuntimeException exception) {
            throw new IllegalStateException(
                    "LangGraph package design or quality audit failed: " + shortMessage(exception),
                    exception
            );
        }
    }

    private ActivityChain toActivityChain(PythonPackageDesignResponse response) {
        PythonPackageDesignData data = response == null ? null : response.getData();
        if (response == null || !response.isSuccess() || data == null
                || !"package-design.v1".equals(data.getSchemaVersion())
                || data.getSteps() == null || data.getSteps().size() < 3 || data.getSteps().size() > 7) {
            throw new IllegalStateException("Python Agent returned an invalid package design");
        }

        List<ActivityStep> steps = new ArrayList<ActivityStep>();
        for (int index = 0; index < data.getSteps().size(); index++) {
            PythonPackageDesignStep source = data.getSteps().get(index);
            if (source == null || !StringUtils.hasText(source.getActivityId())
                    || !StringUtils.hasText(source.getNodeType()) || !StringUtils.hasText(source.getTitle())) {
                throw new IllegalStateException("Python Agent returned an invalid design step");
            }
            ActivityStep step = new ActivityStep(source.getTitle(), source.getActivityId(), source.getNodeType(),
                    index + 1, source.getComponentKeys() == null
                            ? new ArrayList<String>() : new ArrayList<String>(source.getComponentKeys()));
            step.setRecommendationReason(source.getRecommendationReason());
            step.setMusicContent(source.getMusicContent());
            step.setResolvedMusicContent(source.getResolvedMusicContent());
            steps.add(step);
        }

        ActivityChain chain = new ActivityChain();
        chain.setTitle(data.getTitle());
        chain.setReasoningSummary(data.getReasoningSummary());
        chain.setSteps(steps);
        PythonPackageDesignMetadata design = data.getDesign();
        if (design != null) {
            chain.setDesignProvider(design.getProvider());
            chain.setDesignModel(design.getModel());
            chain.setDesignFallbackReason(design.getFallbackReason());
            chain.setDesignTraceId(design.getTraceId());
        }
        if (!StringUtils.hasText(chain.getDesignProvider())) {
            throw new IllegalStateException("Python Agent response omitted design provider");
        }
        return chain;
    }

    private ActivityChain fallback(ParsedLesson parsedLesson, GeneratePreferences preferences, String reason) {
        ActivityChain chain = activityChainGenerator.generate(parsedLesson, preferences);
        chain.setDesignProvider("java_rule_fallback");
        chain.setDesignFallbackReason(reason);
        chain.setReasoningSummary("互动包设计 Agent 不可用，本次使用 Java 规则模板生成。");
        return chain;
    }

    private String shortMessage(Throwable throwable) {
        String message = throwable == null ? null : throwable.getMessage();
        if (!StringUtils.hasText(message)) return "Python package design Agent call failed";
        return message.length() <= 300 ? message : message.substring(0, 300);
    }
}
