package com.buyilehu.musicagent.application.dto.request;

import java.util.HashMap;
import java.util.Map;
import javax.validation.constraints.Min;

/**
 * 学生完成某个活动节点后，向后端提交结果用的请求类
 */
public class StudentNodeSubmitRequest {
    private String resultType = "activity_result";
    @Min(0)
    private Integer score;
    @Min(0)
    private Integer wrongCount = 0;
    @Min(0)
    private Integer hintUsedCount = 0;
    @Min(0)
    private Integer durationSeconds = 0;
    private Map<String, Object> resultJson = new HashMap<>();

    public String getResultType() { return resultType; }
    public void setResultType(String resultType) { this.resultType = resultType; }
    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public Integer getWrongCount() { return wrongCount; }
    public void setWrongCount(Integer wrongCount) { this.wrongCount = wrongCount; }
    public Integer getHintUsedCount() { return hintUsedCount; }
    public void setHintUsedCount(Integer hintUsedCount) { this.hintUsedCount = hintUsedCount; }
    public Integer getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(Integer durationSeconds) { this.durationSeconds = durationSeconds; }
    public Map<String, Object> getResultJson() { return resultJson; }
    public void setResultJson(Map<String, Object> resultJson) { this.resultJson = resultJson; }
}
