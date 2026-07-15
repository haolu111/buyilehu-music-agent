package com.buyilehu.musicagent.infrastructure.lock;

import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.config.DistributedLockProperties;
import java.util.Collections;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import javax.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.distributed-lock", name = "enabled", havingValue = "true", matchIfMissing = true)
public class RedisDistributedLockManager implements DistributedLockManager {
    private static final Logger log = LoggerFactory.getLogger(RedisDistributedLockManager.class);
    private static final DefaultRedisScript<Long> RELEASE_SCRIPT = new DefaultRedisScript<>(
            "if redis.call('get', KEYS[1]) == ARGV[1] then "
                    + "return redis.call('del', KEYS[1]) else return 0 end",
            Long.class);
    private static final DefaultRedisScript<Long> RENEW_SCRIPT = new DefaultRedisScript<>(
            "if redis.call('get', KEYS[1]) == ARGV[1] then "
                    + "return redis.call('pexpire', KEYS[1], ARGV[2]) else return 0 end",
            Long.class);

    private final StringRedisTemplate redisTemplate;
    private final DistributedLockProperties properties;
    private final ScheduledExecutorService renewalExecutor = Executors.newSingleThreadScheduledExecutor(runnable -> {
        Thread thread = new Thread(runnable, "redis-lock-renewal");
        thread.setDaemon(true);
        return thread;
    });

    public RedisDistributedLockManager(StringRedisTemplate redisTemplate,
                                       DistributedLockProperties properties) {
        this.redisTemplate = redisTemplate;
        this.properties = properties;
    }

    @Override
    public <T> T executeWithLock(String resourceKey, Supplier<T> action) {
        String key = properties.getKeyPrefix() + resourceKey;
        String token = UUID.randomUUID().toString();
        acquire(key, token);
        ScheduledFuture<?> renewal = scheduleRenewal(key, token);
        try {
            return action.get();
        } finally {
            renewal.cancel(false);
            release(key, token);
        }
    }

    private ScheduledFuture<?> scheduleRenewal(String key, String token) {
        long intervalMillis = Math.max(100L, properties.getLeaseTimeout().toMillis() / 3L);
        return renewalExecutor.scheduleAtFixedRate(
                () -> renew(key, token), intervalMillis, intervalMillis, TimeUnit.MILLISECONDS);
    }

    private void renew(String key, String token) {
        try {
            Long renewed = redisTemplate.execute(
                    RENEW_SCRIPT,
                    Collections.singletonList(key),
                    token,
                    String.valueOf(properties.getLeaseTimeout().toMillis()));
            if (!Long.valueOf(1L).equals(renewed)) {
                log.warn("Distributed lock {} could not be renewed", key);
            }
        } catch (RuntimeException exception) {
            log.error("Unable to renew distributed lock {}", key, exception);
        }
    }

    private void acquire(String key, String token) {
        long deadline = System.nanoTime() + properties.getWaitTimeout().toNanos();
        do {
            try {
                Boolean acquired = redisTemplate.opsForValue()
                        .setIfAbsent(key, token, properties.getLeaseTimeout());
                if (Boolean.TRUE.equals(acquired)) {
                    return;
                }
            } catch (RuntimeException exception) {
                throw new BusinessException(ErrorCode.DEPENDENCY_UNAVAILABLE, "Redis 分布式锁不可用");
            }

            if (System.nanoTime() >= deadline) {
                throw new BusinessException(ErrorCode.CONFLICT, "资源正在被其他请求修改，请稍后重试");
            }
            sleepBeforeRetry();
        } while (true);
    }

    private void sleepBeforeRetry() {
        try {
            TimeUnit.NANOSECONDS.sleep(properties.getRetryInterval().toNanos());
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            throw new BusinessException(ErrorCode.CONFLICT, "等待分布式锁时请求被中断");
        }
    }

    private void release(String key, String token) {
        try {
            redisTemplate.execute(RELEASE_SCRIPT, Collections.singletonList(key), token);
        } catch (RuntimeException exception) {
            log.error("Unable to release distributed lock {}", key, exception);
        }
    }

    @PreDestroy
    public void shutdownRenewalExecutor() {
        renewalExecutor.shutdownNow();
    }
}
