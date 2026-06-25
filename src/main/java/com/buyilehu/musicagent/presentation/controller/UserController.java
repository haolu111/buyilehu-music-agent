package com.buyilehu.musicagent.presentation.controller;

import com.buyilehu.musicagent.application.dto.response.UserResponse;
import com.buyilehu.musicagent.application.service.UserService;
import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.constraints.Positive;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ApiResponse<UserResponse> getById(@PathVariable @Positive Long id) {
        return ApiResponse.success(userService.getById(id));
    }
}
