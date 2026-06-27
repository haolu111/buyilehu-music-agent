package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.ProposalCardResponse;

public interface ProposalCardService {
    ProposalCardResponse getProposal(Long packageId);

    ProposalCardResponse confirmProposal(Long packageId);
}
