package com.buyilehu.musicagent.common.utils;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public final class PasswordUtils {
    private static final BCryptPasswordEncoder PASSWORD_ENCODER = new BCryptPasswordEncoder();

    private PasswordUtils() {
    }

    public static String encode(String rawPassword) {
        return PASSWORD_ENCODER.encode(rawPassword);
    }

    public static boolean matches(String rawPassword, String encodedPassword) {
        return rawPassword != null
                && encodedPassword != null
                && PASSWORD_ENCODER.matches(rawPassword, encodedPassword);
    }
}
