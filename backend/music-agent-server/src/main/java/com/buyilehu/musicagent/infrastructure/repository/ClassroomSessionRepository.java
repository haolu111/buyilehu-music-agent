package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ClassroomSessionRepository extends JpaRepository<ClassroomSession, Long> {
    Optional<ClassroomSession> findByIdAndTeacherId(Long id, Long teacherId);

    List<ClassroomSession> findByClassIdInAndStatusInOrderByIdDesc(Collection<Long> classIds, Collection<String> statuses);
}
