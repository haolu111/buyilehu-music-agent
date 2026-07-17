package com.buyilehu.musicagent.application.dto.response;

public class LoginResponse {
    private final String token;
    private final String tokenType;
    private final Long expiresIn;
    private final UserResponse user;

    public LoginResponse(String token, String tokenType, Long expiresIn, UserResponse user) {
        this.token = token;
        this.tokenType = tokenType;
        this.expiresIn = expiresIn;
        this.user = user;
    }

    public String getToken() { return token; }
    public String getTokenType() { return tokenType; }
    public Long getExpiresIn() { return expiresIn; }
    public UserResponse getUser() { return user; }
}
