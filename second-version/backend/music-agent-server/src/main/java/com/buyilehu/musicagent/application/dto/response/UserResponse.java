package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.User;

public class UserResponse {
    private final Long id;
    private final String username;
    private final String realName;
    private final String role;
    private final String phone;
    private final String avatarUrl;
    private final String status;

    public UserResponse(Long id, String username, String realName, String role,
                        String phone, String avatarUrl, String status) {
        this.id = id;
        this.username = username;
        this.realName = realName;
        this.role = role;
        this.phone = phone;
        this.avatarUrl = avatarUrl;
        this.status = status;
    }

    public static UserResponse from(User user) {
        return new UserResponse(user.getId(), user.getUsername(), user.getRealName(),
                user.getRole().name(), user.getPhone(), user.getAvatarUrl(), user.getStatus().name());
    }

    public Long getId() { return id; }
    public String getUsername() { return username; }
    public String getRealName() { return realName; }
    public String getRole() { return role; }
    public String getPhone() { return phone; }
    public String getAvatarUrl() { return avatarUrl; }
    public String getStatus() { return status; }
}
