package com.buyilehu.musicagent.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Qualifier;

@Configuration
@ConditionalOnProperty(prefix = "app.async-generation", name = "enabled", havingValue = "true", matchIfMissing = true)
public class RabbitGenerationConfig {
    @Bean
    DirectExchange generationExchange(AsyncGenerationProperties properties) {
        return new DirectExchange(properties.getExchange(), true, false);
    }

    @Bean
    Queue generationQueue(AsyncGenerationProperties properties) {
        return QueueBuilder.durable(properties.getQueue())
                .deadLetterExchange(properties.getDeadLetterExchange())
                .deadLetterRoutingKey(properties.getRoutingKey())
                .build();
    }

    @Bean
    Binding generationBinding(@Qualifier("generationQueue") Queue generationQueue,
                              @Qualifier("generationExchange") DirectExchange generationExchange,
                              AsyncGenerationProperties properties) {
        return BindingBuilder.bind(generationQueue).to(generationExchange).with(properties.getRoutingKey());
    }

    @Bean
    DirectExchange generationDeadLetterExchange(AsyncGenerationProperties properties) {
        return new DirectExchange(properties.getDeadLetterExchange(), true, false);
    }

    @Bean
    Queue generationDeadLetterQueue(AsyncGenerationProperties properties) {
        return QueueBuilder.durable(properties.getDeadLetterQueue()).build();
    }

    @Bean
    Binding generationDeadLetterBinding(
                                        @Qualifier("generationDeadLetterQueue") Queue generationDeadLetterQueue,
                                        @Qualifier("generationDeadLetterExchange") DirectExchange generationDeadLetterExchange,
                                        AsyncGenerationProperties properties) {
        return BindingBuilder.bind(generationDeadLetterQueue)
                .to(generationDeadLetterExchange)
                .with(properties.getRoutingKey());
    }

    @Bean
    MessageConverter generationMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }
}
