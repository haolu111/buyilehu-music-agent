package com.buyilehu.musicagent.infrastructure.capability;

public class PythonCapabilityException extends RuntimeException {
    private final ErrorType errorType;
    private final Integer statusCode;
    private final String remoteCode;
    private final String remoteMessage;

    public PythonCapabilityException(ErrorType errorType, String message) {
        this(errorType, message, null, null, null, null);
    }

    public PythonCapabilityException(ErrorType errorType, String message, Throwable cause) {
        this(errorType, message, null, null, null, cause);
    }

    public PythonCapabilityException(
            ErrorType errorType,
            String message,
            Integer statusCode,
            String remoteCode,
            String remoteMessage,
            Throwable cause
    ) {
        super(message, cause);
        this.errorType = errorType;
        this.statusCode = statusCode;
        this.remoteCode = remoteCode;
        this.remoteMessage = remoteMessage;
    }

    public ErrorType getErrorType() {
        return errorType;
    }

    public Integer getStatusCode() {
        return statusCode;
    }

    public String getRemoteCode() {
        return remoteCode;
    }

    public String getRemoteMessage() {
        return remoteMessage;
    }

    public enum ErrorType {
        DISABLED,
        CONNECTION_FAILED,
        TIMEOUT,
        CLIENT_ERROR,
        SERVER_ERROR,
        RESPONSE_PARSE_ERROR
    }
}
