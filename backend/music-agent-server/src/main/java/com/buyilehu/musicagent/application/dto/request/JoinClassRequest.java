package com.buyilehu.musicagent.application.dto.request;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

public class JoinClassRequest {
    @NotBlank(message = "邀请码不能为空")
    @Size(max = 16, message = "邀请码不能超过16个字符")
    private String inviteCode;

    public String getInviteCode() { return inviteCode; }
    public void setInviteCode(String inviteCode) { this.inviteCode = inviteCode; }
}
