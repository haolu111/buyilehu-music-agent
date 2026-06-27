package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.request.LoginRequest;
import com.buyilehu.musicagent.application.dto.response.LoginResponse;
import com.buyilehu.musicagent.application.dto.response.UserResponse;
import com.buyilehu.musicagent.application.service.AuthService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ApiResponse.success(authService.login(request));
    }

    @GetMapping("/me")
    public ApiResponse<UserResponse> me() {
        return ApiResponse.success(authService.me());
    }
}
