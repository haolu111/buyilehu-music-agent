package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.LoginRequest;
import com.buyilehu.musicagent.application.dto.response.LoginResponse;
import com.buyilehu.musicagent.application.dto.response.UserResponse;
import com.buyilehu.musicagent.application.service.AuthService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.common.utils.JwtUtils;
import com.buyilehu.musicagent.common.utils.PasswordUtils;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserStatus;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
public class AuthServiceImpl implements AuthService {
    private static final Logger log = LoggerFactory.getLogger(AuthServiceImpl.class);

    private final UserRepository userRepository;
    private final JwtUtils jwtUtils;

    public AuthServiceImpl(UserRepository userRepository, JwtUtils jwtUtils) {
        this.userRepository = userRepository;
        this.jwtUtils = jwtUtils;
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> {
                    log.warn("Login failed: user not found, username={}", request.getUsername());
                    return new BusinessException(ErrorCode.UNAUTHORIZED, "用户名或密码错误");
                });

        if (!PasswordUtils.matches(request.getPassword(), user.getPasswordHash())) {
            log.warn("Login failed: password mismatch, username={}", request.getUsername());
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "用户名或密码错误");
        }
        if (user.getStatus() != UserStatus.active) {
            log.warn("Login failed: account disabled, username={}, userId={}", user.getUsername(), user.getId());
            throw new BusinessException(ErrorCode.FORBIDDEN, "账号已被禁用");
        }

        log.info("Login success: userId={}, username={}, role={}", user.getId(), user.getUsername(), user.getRole());
        String token = jwtUtils.generateToken(user.getId(), user.getUsername(), user.getRole().name());
        return new LoginResponse(token, "Bearer", jwtUtils.getExpirationSeconds(), UserResponse.from(user));
    }

    @Override
    public UserResponse me() {
        User user = userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "登录用户不存在"));
        return UserResponse.from(user);
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
    }
}
