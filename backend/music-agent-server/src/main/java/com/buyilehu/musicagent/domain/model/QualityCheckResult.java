package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class QualityCheckResult {
    private Integer score = 100;
    private String status = "passed";
    private List<String> messages = new ArrayList<>();

    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public List<String> getMessages() { return messages; }
    public void setMessages(List<String> messages) { this.messages = messages; }
}
