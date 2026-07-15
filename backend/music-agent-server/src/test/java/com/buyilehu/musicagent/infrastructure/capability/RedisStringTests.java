package com.buyilehu.musicagent.infrastructure.capability;

import com.buyilehu.musicagent.config.DistributedLockProperties;
import com.buyilehu.musicagent.infrastructure.lock.RedisDistributedLockManager;
import java.time.Duration;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.redis.DataRedisTest;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * @Author LuHao
 * @Description Redis String测试
 * @Date 15:13 2026-07-14
 */
@DataRedisTest(properties = "spring.data.redis.repositories.enabled=false")
@Testcontainers(disabledWithoutDocker = true)
class RedisStringTests {
    private static final String TEST_KEY = "test:redis:string:name";

    @Container
    private static final GenericContainer<?> REDIS = new GenericContainer<>("redis:7.2-alpine")
            .withExposedPorts(6379);

    @Autowired
    private StringRedisTemplate redisTemplate;

    @DynamicPropertySource
    static void redisProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.redis.host", REDIS::getHost);
        registry.add("spring.redis.port", () -> REDIS.getMappedPort(6379));
        registry.add("spring.redis.password", () -> "");
        registry.add("spring.redis.database", () -> 0);
    }

    @Test
    void testString() {
        // 写入一条String数据
        redisTemplate.opsForValue().set(TEST_KEY, "虎哥123");

        String name = redisTemplate.opsForValue().get(TEST_KEY);

        assertThat(name).isEqualTo("虎哥123");
    }

    @Test
    void distributedLockReleasesOnlyItsOwnToken() {
        DistributedLockProperties properties = new DistributedLockProperties();
        properties.setKeyPrefix("test:lock:");
        properties.setWaitTimeout(Duration.ofMillis(100));
        properties.setLeaseTimeout(Duration.ofSeconds(5));
        RedisDistributedLockManager lockManager = new RedisDistributedLockManager(redisTemplate, properties);

        String result = lockManager.executeWithLock("package:1", () -> {
            assertThat(redisTemplate.opsForValue().get("test:lock:package:1")).isNotBlank();
            return "done";
        });

        assertThat(result).isEqualTo("done");
        assertThat(redisTemplate.hasKey("test:lock:package:1")).isFalse();
    }

    @AfterEach
    void cleanUp() {
        redisTemplate.delete(TEST_KEY);
    }
}
