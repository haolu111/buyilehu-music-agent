package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SessionNodeStateRepository extends JpaRepository<SessionNodeState, Long> {
    List<SessionNodeState> findBySessionId(Long sessionId);

    Optional<SessionNodeState> findBySessionIdAndActivityNodeId(Long sessionId, Long activityNodeId);
}
