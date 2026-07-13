package com.buyilehu.musicagent.infrastructure.capability;

import java.net.SocketTimeoutException;
import java.time.Duration;

import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonRuntimeBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonPackageBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonPackageDesignRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonActivityAssessmentRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityAssessmentResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityPackageBuildResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonPackageDesignResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityError;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityErrorResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityHealthResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityRuntimeBuildResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityToolkitsResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.core.NestedExceptionUtils;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@Component
public class PythonCapabilityClient {
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final PythonCapabilityProperties properties;

    @Autowired
    public PythonCapabilityClient(
            RestTemplateBuilder restTemplateBuilder,
            ObjectMapper objectMapper,
            PythonCapabilityProperties properties
    ) {
        this(
                restTemplateBuilder
                        .setConnectTimeout(Duration.ofMillis(properties.getConnectTimeoutMs()))
                        .setReadTimeout(Duration.ofMillis(properties.getReadTimeoutMs()))
                        .build(),
                objectMapper,
                properties
        );
    }

    PythonCapabilityClient(RestTemplate restTemplate, ObjectMapper objectMapper, PythonCapabilityProperties properties) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
        this.properties = properties;
    }

    public PythonCapabilityHealthResponse getHealth() {
        return exchange("/api/v1/health", HttpMethod.GET, null, PythonCapabilityHealthResponse.class);
    }

    public PythonCapabilityToolkitsResponse getToolkits() {
        return exchange("/api/v1/toolkits", HttpMethod.GET, null, PythonCapabilityToolkitsResponse.class);
    }

    public PythonCapabilityRuntimeBuildResponse buildRuntime(PythonRuntimeBuildRequest request) {
        return exchange("/api/v1/runtime/build", HttpMethod.POST, request, PythonCapabilityRuntimeBuildResponse.class);
    }

    public PythonCapabilityPackageBuildResponse buildPackage(PythonPackageBuildRequest request) {
        return exchange("/api/v1/packages/build", HttpMethod.POST, request, PythonCapabilityPackageBuildResponse.class);
    }

    public PythonPackageDesignResponse designPackage(PythonPackageDesignRequest request) {
        return exchange("/api/v1/packages/design", HttpMethod.POST, request, PythonPackageDesignResponse.class);
    }

    public PythonCapabilityAssessmentResponse assessActivity(PythonActivityAssessmentRequest request) {
        return exchange("/api/v1/assessments/grade", HttpMethod.POST, request, PythonCapabilityAssessmentResponse.class);
    }

    private <T> T exchange(String path, HttpMethod method, Object payload, Class<T> responseType) {
        ensureEnabled();
        HttpEntity<?> requestEntity = payload == null
                ? new HttpEntity<Object>(defaultHeaders())
                : new HttpEntity<Object>(payload, defaultHeaders());
        try {
            ResponseEntity<String> response = restTemplate.exchange(buildUrl(path), method, requestEntity, String.class);
            return readResponseBody(response.getBody(), responseType, path);
        } catch (HttpStatusCodeException ex) {
            throw mapHttpStatusException(path, ex);
        } catch (ResourceAccessException ex) {
            throw mapResourceAccessException(path, ex);
        } catch (JsonProcessingException ex) {
            throw new PythonCapabilityException(
                    PythonCapabilityException.ErrorType.RESPONSE_PARSE_ERROR,
                    "Failed to parse Python capability response from " + path,
                    ex
            );
        }
    }

    private void ensureEnabled() {
        if (!properties.isEnabled()) {
            throw new PythonCapabilityException(
                    PythonCapabilityException.ErrorType.DISABLED,
                    "Python capability client is disabled by configuration."
            );
        }
    }

    private String buildUrl(String path) {
        String baseUrl = properties.getBaseUrl() == null ? "" : properties.getBaseUrl().trim();
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }
        return baseUrl + path;
    }

    private HttpHeaders defaultHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setAccept(MediaType.parseMediaTypes(MediaType.APPLICATION_JSON_VALUE));
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }

    private <T> T readResponseBody(String body, Class<T> responseType, String path) throws JsonProcessingException {
        if (!StringUtils.hasText(body)) {
            throw new PythonCapabilityException(
                    PythonCapabilityException.ErrorType.RESPONSE_PARSE_ERROR,
                    "Python capability response body is empty for " + path
            );
        }
        return objectMapper.readValue(body, responseType);
    }

    private PythonCapabilityException mapHttpStatusException(String path, HttpStatusCodeException ex) {
        PythonCapabilityErrorResponse errorResponse = tryReadError(ex.getResponseBodyAsString());
        PythonCapabilityError error = errorResponse == null ? null : errorResponse.getError();
        PythonCapabilityException.ErrorType errorType = ex.getStatusCode().is4xxClientError()
                ? PythonCapabilityException.ErrorType.CLIENT_ERROR
                : PythonCapabilityException.ErrorType.SERVER_ERROR;
        String message = error != null && StringUtils.hasText(error.getMessage())
                ? error.getMessage()
                : "Python capability request failed for " + path + " with status " + ex.getRawStatusCode();
        return new PythonCapabilityException(
                errorType,
                message,
                ex.getRawStatusCode(),
                error == null ? null : error.getCode(),
                error == null ? null : error.getMessage(),
                ex
        );
    }

    private PythonCapabilityException mapResourceAccessException(String path, ResourceAccessException ex) {
        Throwable rootCause = NestedExceptionUtils.getMostSpecificCause(ex);
        boolean timeout = rootCause instanceof SocketTimeoutException
                || containsTimeoutMessage(rootCause)
                || containsTimeoutMessage(ex);
        PythonCapabilityException.ErrorType errorType = timeout
                ? PythonCapabilityException.ErrorType.TIMEOUT
                : PythonCapabilityException.ErrorType.CONNECTION_FAILED;
        String message = timeout
                ? "Python capability request timed out for " + path
                : "Failed to connect to Python capability service for " + path;
        return new PythonCapabilityException(errorType, message, ex);
    }

    private boolean containsTimeoutMessage(Throwable throwable) {
        return throwable != null && containsTimeoutMessage(throwable.getMessage());
    }

    private boolean containsTimeoutMessage(String message) {
        String normalized = message == null ? "" : message.toLowerCase();
        return normalized.contains("timed out");
    }

    private PythonCapabilityErrorResponse tryReadError(String body) {
        if (!StringUtils.hasText(body)) {
            return null;
        }
        try {
            return objectMapper.readValue(body, PythonCapabilityErrorResponse.class);
        } catch (Exception ex) {
            return null;
        }
    }
}
