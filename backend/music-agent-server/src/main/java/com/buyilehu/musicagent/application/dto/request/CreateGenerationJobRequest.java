package com.buyilehu.musicagent.application.dto.request;

import com.buyilehu.musicagent.domain.model.GeneratePreferences;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;

public class CreateGenerationJobRequest {
    @NotNull(message = "教案ID不能为空")
    @Positive(message = "教案ID必须为正数")
    private Long lessonPlanId;

    @Valid
    private GeneratePreferences preferences = new GeneratePreferences();

    public Long getLessonPlanId() { return lessonPlanId; }
    public void setLessonPlanId(Long lessonPlanId) { this.lessonPlanId = lessonPlanId; }
    public GeneratePreferences getPreferences() { return preferences; }
    public void setPreferences(GeneratePreferences preferences) { this.preferences = preferences; }
}
