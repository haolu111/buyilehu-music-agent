package com.buyilehu.musicagent.infrastructure.capability.dto.request;

import java.util.LinkedHashMap;
import java.util.Map;

public class PythonPackageDesignRequest {
    private Map<String, Object> lesson = new LinkedHashMap<String, Object>();
    private Map<String, Object> preferences = new LinkedHashMap<String, Object>();

    public Map<String, Object> getLesson() { return lesson; }
    public void setLesson(Map<String, Object> lesson) { this.lesson = lesson; }
    public Map<String, Object> getPreferences() { return preferences; }
    public void setPreferences(Map<String, Object> preferences) { this.preferences = preferences; }
}
