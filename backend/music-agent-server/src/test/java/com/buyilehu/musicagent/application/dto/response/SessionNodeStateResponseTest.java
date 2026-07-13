package com.buyilehu.musicagent.application.dto.response;

import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.SessionNodeState;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class SessionNodeStateResponseTest {
    @Test
    void shouldExposeOnlyVersionedActivityRuntime() {
        ActivityNode node = new ActivityNode();
        node.setNodeType("rhythm_game");
        node.setConfigJson("{\"toolkit\":{\"internal\":true},\"activityRuntime\":{\"schemaVersion\":\"activity-runtime.v1\",\"renderer\":\"rhythm-drag\",\"props\":{\"maxBeats\":4}}}");
        SessionNodeState state = new SessionNodeState();
        state.setActivityNodeId(2L);

        SessionNodeStateResponse response = SessionNodeStateResponse.from(state, node);

        assertThat(response.getRuntimeConfig()).containsEntry("renderer", "rhythm-drag");
        assertThat(response.getRuntimeConfig()).doesNotContainKey("toolkit");
    }

    @Test
    void shouldIgnoreUnsupportedRuntimeSchema() {
        ActivityNode node = new ActivityNode();
        node.setConfigJson("{\"activityRuntime\":{\"schemaVersion\":\"activity-runtime.v0\"}}");

        assertThat(SessionNodeStateResponse.from(new SessionNodeState(), node).getRuntimeConfig()).isNull();
    }
}
