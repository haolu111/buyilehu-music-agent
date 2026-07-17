package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.StudentProgress;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentProgressRepository extends JpaRepository<StudentProgress, Long> {
    Optional<StudentProgress> findBySessionIdAndStudentIdAndCurrentNodeId(Long sessionId, Long studentId, Long currentNodeId);

    List<StudentProgress> findBySessionIdAndStudentId(Long sessionId, Long studentId);

    List<StudentProgress> findBySessionId(Long sessionId);
}