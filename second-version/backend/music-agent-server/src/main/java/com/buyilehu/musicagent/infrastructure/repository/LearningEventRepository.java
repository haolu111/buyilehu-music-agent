package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.LearningEvent;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LearningEventRepository extends JpaRepository<LearningEvent, Long> {
    List<LearningEvent> findBySessionIdAndStudentIdOrderByOccurredAtDesc(Long sessionId, Long studentId);

    List<LearningEvent> findBySessionIdOrderByOccurredAtDesc(Long sessionId);
}