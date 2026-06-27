package com.buyilehu.musicagent.domain.model;

import java.util.ArrayList;
import java.util.List;

public class ParsedLesson {
    private String courseName = "未识别课程名";
    private String grade = "未识别年级";
    private List<String> objectives = new ArrayList<>();
    private List<String> keyPoints = new ArrayList<>();
    private List<String> process = new ArrayList<>();
    private List<String> musicElements = new ArrayList<>();

    public static ParsedLesson fallback() {
        return new ParsedLesson();
    }

    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public String getGrade() { return grade; }
    public void setGrade(String grade) { this.grade = grade; }
    public List<String> getObjectives() { return objectives; }
    public void setObjectives(List<String> objectives) { this.objectives = objectives; }
    public List<String> getKeyPoints() { return keyPoints; }
    public void setKeyPoints(List<String> keyPoints) { this.keyPoints = keyPoints; }
    public List<String> getProcess() { return process; }
    public void setProcess(List<String> process) { this.process = process; }
    public List<String> getMusicElements() { return musicElements; }
    public void setMusicElements(List<String> musicElements) { this.musicElements = musicElements; }
}
