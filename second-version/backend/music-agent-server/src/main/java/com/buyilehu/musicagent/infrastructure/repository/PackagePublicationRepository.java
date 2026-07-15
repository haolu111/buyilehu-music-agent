package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.PackagePublication;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PackagePublicationRepository extends JpaRepository<PackagePublication, Long> {
    Optional<PackagePublication> findByIdAndPublishedBy(Long id, Long publishedBy);
}
