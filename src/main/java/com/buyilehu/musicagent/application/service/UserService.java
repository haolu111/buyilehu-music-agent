package com.buyilehu.musicagent.application.service;

import com.buyilehu.musicagent.application.dto.response.UserResponse;

public interface UserService {
    UserResponse getById(Long id);
}
