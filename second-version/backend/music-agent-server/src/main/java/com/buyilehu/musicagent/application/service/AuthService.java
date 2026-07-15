package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.request.LoginRequest;
import com.buyilehu.musicagent.application.dto.response.LoginResponse;
import com.buyilehu.musicagent.application.dto.response.UserResponse;

public interface AuthService {
    LoginResponse login(LoginRequest request);

    UserResponse me();
}
