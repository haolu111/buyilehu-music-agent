package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.ProposalCard;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ProposalCardRepository extends JpaRepository<ProposalCard, Long> {
    List<ProposalCard> findByPackageId(Long packageId);
    Optional<ProposalCard> findFirstByPackageIdOrderByIdDesc(Long packageId);
}
