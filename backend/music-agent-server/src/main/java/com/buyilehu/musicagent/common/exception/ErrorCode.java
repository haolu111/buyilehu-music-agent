package com.buyilehu.musicagent.common.exception;

public enum ErrorCode {
    PARAM_ERROR(40001, "参数错误"),
    BAD_REQUEST(40000, "请求参数错误"),
    UNAUTHORIZED(40100, "未登录或登录已失效"),
    FORBIDDEN(40300, "无权访问该资源"),
    ACTIVITY_LOCKED(40301, "当前活动尚未由老师开启"),
    RESOURCE_NOT_FOUND(40400, "资源不存在"),
    CONFLICT(40900, "资源状态冲突"),
    DEPENDENCY_UNAVAILABLE(50300, "依赖服务暂不可用"),
    INTERNAL_ERROR(50000, "服务器内部错误");

    private final int code;
    private final String message;

    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int code() {
        return code;
    }

    public String message() {
        return message;
    }
}
