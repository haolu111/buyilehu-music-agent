package com.buyilehu.musicagent.infrastructure.status;

import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.config.AsyncGenerationProperties;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Optional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "true", matchIfMissing = true)
public class RedisGenerationJobStatusStore implements GenerationJobStatusStore {
    private static final String KEY_PREFIX = "music-agent:generation:status:";

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;
    private final AsyncGenerationProperties properties;

    public RedisGenerationJobStatusStore(StringRedisTemplate redisTemplate, ObjectMapper objectMapper,
                                         AsyncGenerationProperties properties) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
        this.properties = properties;
    }

    @Override
    public void save(GenerationJobStatus status) {
        try {
            String payload = objectMapper.writeValueAsString(status);
            redisTemplate.opsForValue().set(KEY_PREFIX + status.getId(), payload, properties.getStatusTtl());
            redisTemplate.convertAndSend(properties.getStatusChannel(), payload);
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Unable to serialize generation status", exception);
        }
    }

    @Override
    public Optional<GenerationJobStatus> find(Long jobId) {
        String payload = redisTemplate.opsForValue().get(KEY_PREFIX + jobId);
        if (payload == null) {
            return Optional.empty();
        }
        try {
            return Optional.of(objectMapper.readValue(payload, GenerationJobStatus.class));
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Unable to deserialize generation status", exception);
        }
    }
}
