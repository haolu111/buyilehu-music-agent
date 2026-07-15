package com.buyilehu.musicagent.infrastructure.lock;

import java.util.function.Supplier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.distributed-lock", name = "enabled", havingValue = "false")
public class NoOpDistributedLockManager implements DistributedLockManager {
    @Override
    public <T> T executeWithLock(String resourceKey, Supplier<T> action) {
        return action.get();
    }
}
