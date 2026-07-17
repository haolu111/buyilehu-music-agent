package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ClassMember;
import com.buyilehu.musicagent.domain.entity.User;

public class ClassStudentResponse {
    private final Long memberId;
    private final Long studentId;
    private final String username;
    private final String realName;
    private final String status;

    public ClassStudentResponse(Long memberId, Long studentId, String username, String realName, String status) {
        this.memberId = memberId;
        this.studentId = studentId;
        this.username = username;
        this.realName = realName;
        this.status = status;
    }

    public static ClassStudentResponse from(ClassMember member, User user) {
        return new ClassStudentResponse(
                member.getId(),
                user.getId(),
                user.getUsername(),
                user.getRealName(),
                member.getStatus());
    }

    public Long getMemberId() { return memberId; }
    public Long getStudentId() { return studentId; }
    public String getUsername() { return username; }
    public String getRealName() { return realName; }
    public String getStatus() { return status; }
}
