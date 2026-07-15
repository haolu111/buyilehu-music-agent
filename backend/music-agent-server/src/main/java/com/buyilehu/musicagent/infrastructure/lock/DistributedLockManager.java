package com.buyilehu.musicagent.infrastructure.lock;

import java.util.function.Supplier;

public interface DistributedLockManager {
    <T> T executeWithLock(String resourceKey, Supplier<T> action);
}
