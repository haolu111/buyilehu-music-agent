package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ClassEntity;

public class ClassResponse {
    private final Long id;
    private final String className;
    private final Long teacherId;
    private final String inviteCode;
    private final String description;
    private final String status;

    public ClassResponse(Long id, String className, Long teacherId, String inviteCode,
                         String description, String status) {
        this.id = id;
        this.className = className;
        this.teacherId = teacherId;
        this.inviteCode = inviteCode;
        this.description = description;
        this.status = status;
    }

    public static ClassResponse from(ClassEntity classEntity) {
        return new ClassResponse(
                classEntity.getId(),
                classEntity.getClassName(),
                classEntity.getTeacherId(),
                classEntity.getInviteCode(),
                classEntity.getDescription(),
                classEntity.getStatus());
    }

    public Long getId() { return id; }
    public String getClassName() { return className; }
    public Long getTeacherId() { return teacherId; }
    public String getInviteCode() { return inviteCode; }
    public String getDescription() { return description; }
    public String getStatus() { return status; }
}
