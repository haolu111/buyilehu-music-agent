package com.buyilehu.musicagent.domain.model;

public class GeneratePreferences {
    private String style = "standard";
    private Integer durationMinutes = 40;

    public String getStyle() { return style; }
    public void setStyle(String style) { this.style = style; }
    public Integer getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(Integer durationMinutes) { this.durationMinutes = durationMinutes; }
}
