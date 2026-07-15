package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.GenerationJob;
import java.util.Optional;
import javax.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface GenerationJobRepository extends JpaRepository<GenerationJob, Long> {
    Optional<GenerationJob> findByCreatedByAndIdempotencyKey(Long createdBy, String idempotencyKey);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select job from GenerationJob job where job.id = :jobId")
    Optional<GenerationJob> findByIdForUpdate(@Param("jobId") Long jobId);
}
