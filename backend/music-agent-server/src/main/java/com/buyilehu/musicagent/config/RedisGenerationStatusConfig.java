package com.buyilehu.musicagent.config;

import com.buyilehu.musicagent.application.dto.response.GenerationJobStatus;
import com.buyilehu.musicagent.application.service.GenerationSseService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.listener.ChannelTopic;
import org.springframework.data.redis.listener.RedisMessageListenerContainer;

@Configuration
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "true", matchIfMissing = true)
public class RedisGenerationStatusConfig {
    private static final Logger log = LoggerFactory.getLogger(RedisGenerationStatusConfig.class);

    @Bean
    RedisMessageListenerContainer generationStatusListenerContainer(
            RedisConnectionFactory connectionFactory,
            AsyncGenerationProperties properties,
            ObjectMapper objectMapper,
            GenerationSseService sseService) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(connectionFactory);
        container.addMessageListener((message, pattern) -> {
            try {
                String payload = new String(message.getBody(), StandardCharsets.UTF_8);
                sseService.broadcast(objectMapper.readValue(payload, GenerationJobStatus.class));
            } catch (Exception exception) {
                log.warn("Unable to broadcast generation status from Redis", exception);
            }
        }, new ChannelTopic(properties.getStatusChannel()));
        return container;
    }
}
