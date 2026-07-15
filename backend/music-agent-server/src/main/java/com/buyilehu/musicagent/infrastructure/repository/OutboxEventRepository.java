package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.OutboxEvent;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import javax.persistence.LockModeType;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface OutboxEventRepository extends JpaRepository<OutboxEvent, Long> {
    Optional<OutboxEvent> findByAggregateTypeAndAggregateIdAndEventType(
            String aggregateType, Long aggregateId, String eventType);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select event from OutboxEvent event where "
            + "(event.status = 'pending' and event.nextAttemptAt <= :now) "
            + "or (event.status = 'processing' and event.lockedAt <= :staleBefore) "
            + "order by event.id")
    List<OutboxEvent> findReadyForDelivery(@Param("now") LocalDateTime now,
                                           @Param("staleBefore") LocalDateTime staleBefore,
                                           Pageable pageable);
}
