package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ClassMember;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ClassMemberRepository extends JpaRepository<ClassMember, Long> {
    boolean existsByClassIdAndUserId(Long classId, Long userId);

    boolean existsByClassIdAndUserIdAndStatus(Long classId, Long userId, String status);

    Optional<ClassMember> findByClassIdAndUserId(Long classId, Long userId);

    List<ClassMember> findByClassIdAndStatusOrderByIdAsc(Long classId, String status);

    List<ClassMember> findByUserIdAndStatusOrderByIdDesc(Long userId, String status);
}
