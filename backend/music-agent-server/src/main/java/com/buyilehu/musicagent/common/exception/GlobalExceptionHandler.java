package com.buyilehu.musicagent.common.exception;

import com.buyilehu.musicagent.common.response.ApiResponse;
import javax.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException exception) {
        ErrorCode errorCode = exception.getErrorCode();
        log.warn("Business exception: code={}, message={}", errorCode.code(), exception.getMessage());
        HttpStatus status = resolveHttpStatus(errorCode);
        return ResponseEntity
                .status(status)
                .body(ApiResponse.fail(errorCode.code(), exception.getMessage()));
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, ConstraintViolationException.class})
    public ResponseEntity<ApiResponse<Void>> handleValidationException(Exception exception) {
        log.warn("Validation failed: {}", exception.getMessage());
        return ResponseEntity
                .badRequest()
                .body(ApiResponse.fail(ErrorCode.PARAM_ERROR.code(), ErrorCode.PARAM_ERROR.message()));
    }

    @ExceptionHandler({ObjectOptimisticLockingFailureException.class, DataIntegrityViolationException.class})
    public ResponseEntity<ApiResponse<Void>> handleStateConflict(Exception exception) {
        log.warn("State conflict: {}", exception.getMessage());
        return ResponseEntity
                .status(HttpStatus.CONFLICT)
                .body(ApiResponse.fail(ErrorCode.CONFLICT.code(), ErrorCode.CONFLICT.message()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleUnexpectedException(Exception exception) {
        log.error("Unhandled server exception", exception);
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.fail(ErrorCode.INTERNAL_ERROR.code(), ErrorCode.INTERNAL_ERROR.message()));
    }

    private HttpStatus resolveHttpStatus(ErrorCode errorCode) {
        switch (errorCode) {
            case PARAM_ERROR:
            case BAD_REQUEST:
                return HttpStatus.BAD_REQUEST;
            case UNAUTHORIZED:
                return HttpStatus.UNAUTHORIZED;
            case FORBIDDEN:
            case ACTIVITY_LOCKED:
                return HttpStatus.FORBIDDEN;
            case RESOURCE_NOT_FOUND:
                return HttpStatus.NOT_FOUND;
            case CONFLICT:
                return HttpStatus.CONFLICT;
            case DEPENDENCY_UNAVAILABLE:
                return HttpStatus.SERVICE_UNAVAILABLE;
            default:
                return HttpStatus.INTERNAL_SERVER_ERROR;
        }
    }
}
