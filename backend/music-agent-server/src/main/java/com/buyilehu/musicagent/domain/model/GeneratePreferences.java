package com.buyilehu.musicagent.domain.model;

/**
 * 生成课堂互动包时的偏好配置对象。目前它包含两个配置：style 控制生成风格，
 * durationMinutes 控制课堂时长。默认值表示教师不额外设置时，系统按标准 40 分钟课堂来生成。
 */


public class GeneratePreferences {
    private String style = "standard";
    private Integer durationMinutes = 40;

    public String getStyle() { return style; }
    public void setStyle(String style) { this.style = style; }
    public Integer getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(Integer durationMinutes) { this.durationMinutes = durationMinutes; }
}
