package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ClassEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ClassRepository extends JpaRepository<ClassEntity, Long> {
    Optional<ClassEntity> findByInviteCode(String inviteCode);

    boolean existsByInviteCode(String inviteCode);

    List<ClassEntity> findByTeacherIdOrderByIdDesc(Long teacherId);
}
