package com.buyilehu.musicagent.domain.model;

import com.fasterxml.jackson.annotation.JsonAlias;

/**
 * 生成课堂互动包时的偏好配置对象。目前它包含两个配置：style 控制生成风格，
 * durationMinutes 控制课堂时长。默认值表示教师不额外设置时，系统按标准 40 分钟课堂来生成。
 */


public class GeneratePreferences {
    private String style = "standard";
    @JsonAlias("duration")
    private Integer durationMinutes = 40;
    private String mode;
    private String density;
    private String difficulty;
    private String flow;
    private String theme;

    public String getStyle() { return style; }
    public void setStyle(String style) { this.style = style; }
    public Integer getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(Integer durationMinutes) { this.durationMinutes = durationMinutes; }
    public String getMode() { return mode; }
    public void setMode(String mode) { this.mode = mode; }
    public String getDensity() { return density; }
    public void setDensity(String density) { this.density = density; }
    public String getDifficulty() { return difficulty; }
    public void setDifficulty(String difficulty) { this.difficulty = difficulty; }
    public String getFlow() { return flow; }
    public void setFlow(String flow) { this.flow = flow; }
    public String getTheme() { return theme; }
    public void setTheme(String theme) { this.theme = theme; }
}
