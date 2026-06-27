package com.buyilehu.musicagent.domain.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "component_definitions")
public class ComponentDefinition extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "component_key", nullable = false, length = 80)
    private String componentKey;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, length = 50)
    private String category;

    @Column(name = "schema_json", columnDefinition = "TEXT")
    private String schemaJson;

    @Column(nullable = false, length = 20)
    private String status = "active";

    public ComponentDefinition() {
    }

    public Long getId() { return id; }
    public String getComponentKey() { return componentKey; }
    public void setComponentKey(String componentKey) { this.componentKey = componentKey; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getSchemaJson() { return schemaJson; }
    public void setSchemaJson(String schemaJson) { this.schemaJson = schemaJson; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
