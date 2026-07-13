package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;

public class PythonCapabilityRuntimeBuildData {
    @JsonProperty("activity_id")
    private String activityId;
    private JsonNode toolkit;
    private JsonNode composition;
    private JsonNode runtime;
    @JsonProperty("media_session_preview")
    private JsonNode mediaSessionPreview;

    public String getActivityId() {
        return activityId;
    }

    public void setActivityId(String activityId) {
        this.activityId = activityId;
    }

    public JsonNode getToolkit() {
        return toolkit;
    }

    public void setToolkit(JsonNode toolkit) {
        this.toolkit = toolkit;
    }

    public JsonNode getComposition() {
        return composition;
    }

    public void setComposition(JsonNode composition) {
        this.composition = composition;
    }

    public JsonNode getRuntime() {
        return runtime;
    }

    public void setRuntime(JsonNode runtime) {
        this.runtime = runtime;
    }

    public JsonNode getMediaSessionPreview() {
        return mediaSessionPreview;
    }

    public void setMediaSessionPreview(JsonNode mediaSessionPreview) {
        this.mediaSessionPreview = mediaSessionPreview;
    }
}
