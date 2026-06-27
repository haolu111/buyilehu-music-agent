package com.buyilehu.musicagent.application.dto.request;

import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class CreateClassroomSessionRequest {
    @NotNull
    @Positive
    private Long publicationId;

    public Long getPublicationId() {
        return publicationId;
    }

    public void setPublicationId(Long publicationId) {
        this.publicationId = publicationId;
    }
}
