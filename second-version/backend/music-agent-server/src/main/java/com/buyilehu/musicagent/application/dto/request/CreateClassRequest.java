package com.buyilehu.musicagent.application.dto.request;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
/*
创建班级类
 */
public class CreateClassRequest {
    @NotBlank(message = "班级名称不能为空")
    @Size(max = 100, message = "班级名称不能超过100个字符")
    private String className;

    @Size(max = 255, message = "班级描述不能超过255个字符")
    private String description;

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
