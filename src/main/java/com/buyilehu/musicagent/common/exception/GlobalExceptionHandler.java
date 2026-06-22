package com.buyilehu.musicagent.common.exception;

import com.buyilehu.musicagent.common.api.ApiResponse;
import javax.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException exception) {
        ErrorCode code = exception.getErrorCode();
        HttpStatus status;
        switch (code) {
            case BAD_REQUEST: status = HttpStatus.BAD_REQUEST; break;
            case UNAUTHORIZED: status = HttpStatus.UNAUTHORIZED; break;
            case FORBIDDEN: status = HttpStatus.FORBIDDEN; break;
            case RESOURCE_NOT_FOUND: status = HttpStatus.NOT_FOUND; break;
            default: status = HttpStatus.INTERNAL_SERVER_ERROR;
        }
        return ResponseEntity.status(status).body(ApiResponse.failure(code.code(), exception.getMessage()));
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, ConstraintViolationException.class})
    public ResponseEntity<ApiResponse<Void>> handleValidationException(Exception exception) {
        return ResponseEntity.badRequest().body(ApiResponse.failure(
                ErrorCode.BAD_REQUEST.code(), ErrorCode.BAD_REQUEST.message()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleUnexpectedException(Exception exception) {
        log.error("Unhandled server exception", exception);
        return ResponseEntity.internalServerError().body(ApiResponse.failure(
                ErrorCode.INTERNAL_ERROR.code(), ErrorCode.INTERNAL_ERROR.message()));
    }
}
