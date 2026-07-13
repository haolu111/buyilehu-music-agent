package com.buyilehu.musicagent.infrastructure.capability;

import java.net.SocketTimeoutException;
import java.util.LinkedHashMap;
import java.util.Map;

import com.buyilehu.musicagent.infrastructure.capability.dto.request.PythonRuntimeBuildRequest;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityHealthResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityRuntimeBuildResponse;
import com.buyilehu.musicagent.infrastructure.capability.dto.response.PythonCapabilityToolkitsResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.ExpectedCount.once;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withBadRequest;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withServerError;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

class PythonCapabilityClientTest {
    private static final String BASE_URL = "http://python-service.test";

    private MockRestServiceServer server;
    private PythonCapabilityClient client;

    @BeforeEach
    void setUp() {
        RestTemplate restTemplate = new RestTemplate();
        server = MockRestServiceServer.bindTo(restTemplate).build();
        client = new PythonCapabilityClient(restTemplate, new ObjectMapper(), enabledProperties());
    }

    @Test
    void shouldGetHealth() {
        server.expect(once(), requestTo(BASE_URL + "/api/v1/health"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(
                        "{\"success\":true,\"data\":{\"status\":\"ok\",\"service\":\"python-capability-library\",\"python_version\":\"3.11.9\"}}",
                        MediaType.APPLICATION_JSON
                ));

        PythonCapabilityHealthResponse response = client.getHealth();

        assertThat(response.isSuccess()).isTrue();
        assertThat(response.getData().getStatus()).isEqualTo("ok");
        assertThat(response.getData().getPythonVersion()).isEqualTo("3.11.9");
        server.verify();
    }

    @Test
    void shouldGetToolkits() {
        server.expect(once(), requestTo(BASE_URL + "/api/v1/toolkits"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(
                        "{\"success\":true,\"data\":{\"count\":1,\"items\":[{\"activity_id\":\"pitch_game\"}]}}",
                        MediaType.APPLICATION_JSON
                ));

        PythonCapabilityToolkitsResponse response = client.getToolkits();

        assertThat(response.isSuccess()).isTrue();
        assertThat(response.getData().getCount()).isEqualTo(1);
        assertThat(response.getData().getItems().isArray()).isTrue();
        assertThat(response.getData().getItems().get(0).get("activity_id").asText()).isEqualTo("pitch_game");
        server.verify();
    }

    @Test
    void shouldPostRuntimeBuildUsingPythonFieldNames() {
        Map<String, Object> composition = new LinkedHashMap<String, Object>();
        composition.put("selected_activity_id", "pitch_game");
        Map<String, Object> requestBody = new LinkedHashMap<String, Object>();
        requestBody.put("student_id", "stu-1");

        PythonRuntimeBuildRequest request = new PythonRuntimeBuildRequest();
        request.setActivityId("pitch_game");
        request.setComposition(composition);
        request.setRequest(requestBody);

        server.expect(once(), requestTo(BASE_URL + "/api/v1/runtime/build"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"activity_id\":\"pitch_game\",\"composition\":{\"selected_activity_id\":\"pitch_game\"},\"request\":{\"student_id\":\"stu-1\"}}"))
                .andRespond(withSuccess(
                        "{\"success\":true,\"data\":{\"activity_id\":\"pitch_game\",\"toolkit\":{},\"composition\":{},\"runtime\":{\"scene\":\"ready\"},\"media_session_preview\":null}}",
                        MediaType.APPLICATION_JSON
                ));

        PythonCapabilityRuntimeBuildResponse response = client.buildRuntime(request);

        assertThat(response.isSuccess()).isTrue();
        assertThat(response.getData().getActivityId()).isEqualTo("pitch_game");
        assertThat(response.getData().getRuntime().get("scene").asText()).isEqualTo("ready");
        server.verify();
    }

    @Test
    void shouldWrapClientErrors() {
        server.expect(once(), requestTo(BASE_URL + "/api/v1/toolkits"))
                .andRespond(withBadRequest().contentType(MediaType.APPLICATION_JSON)
                        .body("{\"success\":false,\"error\":{\"code\":\"invalid_request\",\"message\":\"bad toolkit request\"}}"));

        assertThatThrownBy(() -> client.getToolkits())
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> {
                    PythonCapabilityException error = (PythonCapabilityException) ex;
                    assertThat(error.getErrorType()).isEqualTo(PythonCapabilityException.ErrorType.CLIENT_ERROR);
                    assertThat(error.getStatusCode()).isEqualTo(400);
                    assertThat(error.getRemoteCode()).isEqualTo("invalid_request");
                    assertThat(error.getRemoteMessage()).isEqualTo("bad toolkit request");
                });
    }

    @Test
    void shouldWrapServerErrors() {
        server.expect(once(), requestTo(BASE_URL + "/api/v1/health"))
                .andRespond(withServerError().contentType(MediaType.APPLICATION_JSON)
                        .body("{\"success\":false,\"error\":{\"code\":\"internal_server_error\",\"message\":\"Unexpected server error.\"}}"));

        assertThatThrownBy(() -> client.getHealth())
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> {
                    PythonCapabilityException error = (PythonCapabilityException) ex;
                    assertThat(error.getErrorType()).isEqualTo(PythonCapabilityException.ErrorType.SERVER_ERROR);
                    assertThat(error.getStatusCode()).isEqualTo(500);
                });
    }

    @Test
    void shouldWrapParseErrors() {
        server.expect(once(), requestTo(BASE_URL + "/api/v1/health"))
                .andRespond(withSuccess("not-json", MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> client.getHealth())
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> assertThat(((PythonCapabilityException) ex).getErrorType())
                        .isEqualTo(PythonCapabilityException.ErrorType.RESPONSE_PARSE_ERROR));
    }

    @Test
    void shouldWrapTimeouts() {
        RestTemplate restTemplate = new RestTemplate() {
            @Override
            protected <T> T doExecute(java.net.URI url, HttpMethod method,
                                      org.springframework.web.client.RequestCallback requestCallback,
                                      org.springframework.web.client.ResponseExtractor<T> responseExtractor) {
                throw new ResourceAccessException("Read timed out", new SocketTimeoutException("Read timed out"));
            }
        };
        PythonCapabilityClient timeoutClient = new PythonCapabilityClient(restTemplate, new ObjectMapper(), enabledProperties());

        assertThatThrownBy(timeoutClient::getHealth)
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> assertThat(((PythonCapabilityException) ex).getErrorType())
                        .isEqualTo(PythonCapabilityException.ErrorType.TIMEOUT));
    }

    @Test
    void shouldWrapConnectionFailures() {
        RestTemplate restTemplate = new RestTemplate() {
            @Override
            protected <T> T doExecute(java.net.URI url, HttpMethod method,
                                      org.springframework.web.client.RequestCallback requestCallback,
                                      org.springframework.web.client.ResponseExtractor<T> responseExtractor) {
                throw new ResourceAccessException("Connection refused");
            }
        };
        PythonCapabilityClient unavailableClient = new PythonCapabilityClient(restTemplate, new ObjectMapper(), enabledProperties());

        assertThatThrownBy(unavailableClient::getHealth)
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> assertThat(((PythonCapabilityException) ex).getErrorType())
                        .isEqualTo(PythonCapabilityException.ErrorType.CONNECTION_FAILED));
    }

    @Test
    void shouldFailWhenDisabled() {
        PythonCapabilityProperties properties = enabledProperties();
        properties.setEnabled(false);
        PythonCapabilityClient disabledClient = new PythonCapabilityClient(new RestTemplate(), new ObjectMapper(), properties);

        assertThatThrownBy(disabledClient::getHealth)
                .isInstanceOf(PythonCapabilityException.class)
                .satisfies(ex -> assertThat(((PythonCapabilityException) ex).getErrorType())
                        .isEqualTo(PythonCapabilityException.ErrorType.DISABLED));
    }

    private PythonCapabilityProperties enabledProperties() {
        PythonCapabilityProperties properties = new PythonCapabilityProperties();
        properties.setEnabled(true);
        properties.setBaseUrl(BASE_URL);
        properties.setConnectTimeoutMs(1000);
        properties.setReadTimeoutMs(3000);
        return properties;
    }
}
