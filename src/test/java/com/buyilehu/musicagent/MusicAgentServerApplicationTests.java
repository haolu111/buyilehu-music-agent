package com.buyilehu.musicagent;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class MusicAgentServerApplicationTests {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void contextLoadsAndHealthEndpointIsPublic() throws Exception {
        mockMvc.perform(get("/api/v1/system/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.status").value("UP"));
    }

    @Test
    void businessEndpointRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/users/1"))
                .andExpect(status().isUnauthorized());
    }
}
