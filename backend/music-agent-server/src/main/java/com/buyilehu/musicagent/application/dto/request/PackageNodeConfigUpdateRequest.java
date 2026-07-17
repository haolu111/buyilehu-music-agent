package com.buyilehu.musicagent.application.dto.request;

import java.util.HashMap;
import java.util.Map;
import javax.validation.constraints.Min;
import javax.validation.constraints.Size;

public class PackageNodeConfigUpdateRequest {
    @Size(max = 120)
    private String title;

    @Size(max = 500)
    private String description;

    private String difficulty;

    @Min(0)
    private Integer rhythmCardCount;

    private Boolean hintEnabled;

    private Boolean hidden;

    private Long componentInstanceId;

    private Map<String, Object> componentParams = new HashMap<>();
    private Map<String, Object> musicContent = new HashMap<>();
    private Map<String, Object> resolvedMusicContent = new HashMap<>();

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getDifficulty() { return difficulty; }
    public void setDifficulty(String difficulty) { this.difficulty = difficulty; }
    public Integer getRhythmCardCount() { return rhythmCardCount; }
    public void setRhythmCardCount(Integer rhythmCardCount) { this.rhythmCardCount = rhythmCardCount; }
    public Boolean getHintEnabled() { return hintEnabled; }
    public void setHintEnabled(Boolean hintEnabled) { this.hintEnabled = hintEnabled; }
    public Boolean getHidden() { return hidden; }
    public void setHidden(Boolean hidden) { this.hidden = hidden; }
    public Long getComponentInstanceId() { return componentInstanceId; }
    public void setComponentInstanceId(Long componentInstanceId) { this.componentInstanceId = componentInstanceId; }
    public Map<String, Object> getComponentParams() { return componentParams; }
    public void setComponentParams(Map<String, Object> componentParams) { this.componentParams = componentParams; }
    public Map<String, Object> getMusicContent() { return musicContent; }
    public void setMusicContent(Map<String, Object> musicContent) { this.musicContent = musicContent; }
    public Map<String, Object> getResolvedMusicContent() { return resolvedMusicContent; }
    public void setResolvedMusicContent(Map<String, Object> resolvedMusicContent) { this.resolvedMusicContent = resolvedMusicContent; }
}
