package com.buyilehu.musicagent.infrastructure.capability.dto.request;

import java.util.HashMap;
import java.util.Map;

public class PythonPackageNodeRevisionRequest {
    private Map<String, Object> lesson = new HashMap<String, Object>();
    private Map<String, Object> node = new HashMap<String, Object>();
    private String feedback;

    public Map<String, Object> getLesson() { return lesson; }
    public void setLesson(Map<String, Object> lesson) { this.lesson = lesson; }
    public Map<String, Object> getNode() { return node; }
    public void setNode(Map<String, Object> node) { this.node = node; }
    public String getFeedback() { return feedback; }
    public void setFeedback(String feedback) { this.feedback = feedback; }
}
