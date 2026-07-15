package com.buyilehu.musicagent.common.utils;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtUtils {
    private static final String HMAC_SHA256 = "HmacSHA256";

    private final String secret;
    private final long expirationSeconds;

    public JwtUtils(
            @Value("${app.jwt.secret:buyilehu-music-agent-dev-secret-change-me}") String secret,
            @Value("${app.jwt.expiration-seconds:86400}") long expirationSeconds) {
        this.secret = secret;
        this.expirationSeconds = expirationSeconds;
    }

    public String generateToken(Long userId, String username, String role) {
        long now = Instant.now().getEpochSecond();
        String header = "{\"alg\":\"HS256\",\"typ\":\"JWT\"}";
        String payload = "{"
                + "\"sub\":\"" + escape(String.valueOf(userId)) + "\","
                + "\"username\":\"" + escape(username) + "\","
                + "\"role\":\"" + escape(role) + "\","
                + "\"iat\":" + now + ","
                + "\"exp\":" + (now + expirationSeconds)
                + "}";

        String unsignedToken = base64Url(header.getBytes(StandardCharsets.UTF_8))
                + "."
                + base64Url(payload.getBytes(StandardCharsets.UTF_8));
        return unsignedToken + "." + sign(unsignedToken);
    }

    public JwtClaims parseToken(String token) {
        if (token == null || token.trim().isEmpty()) {
            throw new IllegalArgumentException("Token is blank");
        }
        String[] parts = token.split("\\.");
        if (parts.length != 3) {
            throw new IllegalArgumentException("Token format is invalid");
        }

        String unsignedToken = parts[0] + "." + parts[1];
        String expectedSignature = sign(unsignedToken);
        if (!MessageDigest.isEqual(expectedSignature.getBytes(StandardCharsets.UTF_8),
                parts[2].getBytes(StandardCharsets.UTF_8))) {
            throw new IllegalArgumentException("Token signature is invalid");
        }

        String payload = new String(Base64.getUrlDecoder().decode(parts[1]), StandardCharsets.UTF_8);
        long expiresAt = Long.parseLong(readJsonValue(payload, "exp"));
        if (expiresAt < Instant.now().getEpochSecond()) {
            throw new IllegalArgumentException("Token is expired");
        }

        return new JwtClaims(
                Long.valueOf(readJsonValue(payload, "sub")),
                readJsonValue(payload, "username"),
                readJsonValue(payload, "role"));
    }

    public long getExpirationSeconds() {
        return expirationSeconds;
    }

    private String sign(String content) {
        try {
            Mac mac = Mac.getInstance(HMAC_SHA256);
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), HMAC_SHA256));
            return base64Url(mac.doFinal(content.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to sign JWT", exception);
        }
    }

    private String base64Url(byte[] bytes) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private String readJsonValue(String json, String key) {
        String quotedKey = "\"" + key + "\":";
        int keyStart = json.indexOf(quotedKey);
        if (keyStart < 0) {
            throw new IllegalArgumentException("Missing claim: " + key);
        }
        int valueStart = keyStart + quotedKey.length();
        if (json.charAt(valueStart) == '"') {
            int valueEnd = json.indexOf('"', valueStart + 1);
            return unescape(json.substring(valueStart + 1, valueEnd));
        }
        int valueEnd = valueStart;
        while (valueEnd < json.length() && Character.isDigit(json.charAt(valueEnd))) {
            valueEnd++;
        }
        return json.substring(valueStart, valueEnd);
    }

    private String escape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private String unescape(String value) {
        return value.replace("\\\"", "\"").replace("\\\\", "\\");
    }

    public static class JwtClaims {
        private final Long userId;
        private final String username;
        private final String role;

        public JwtClaims(Long userId, String username, String role) {
            this.userId = userId;
            this.username = username;
            this.role = role;
        }

        public Long getUserId() { return userId; }
        public String getUsername() { return username; }
        public String getRole() { return role; }
    }
}
