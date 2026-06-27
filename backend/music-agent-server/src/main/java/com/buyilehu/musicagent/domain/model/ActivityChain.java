package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class ActivityChain {
    private String title;
    private List<ActivityStep> steps = new ArrayList<>();

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public List<ActivityStep> getSteps() { return steps; }
    public void setSteps(List<ActivityStep> steps) { this.steps = steps; }
}
