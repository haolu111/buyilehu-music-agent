package com.buyilehu.musicagent.infrastructure.capability.dto.response;

import com.fasterxml.jackson.databind.JsonNode;

public class PythonCapabilityToolkitsData {
    private int count;
    private JsonNode items;

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    public JsonNode getItems() {
        return items;
    }

    public void setItems(JsonNode items) {
        this.items = items;
    }
}
