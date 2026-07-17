package com.buyilehu.musicagent.domain.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "component_instances")
public class ComponentInstance extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "activity_node_id", nullable = false)
    private Long activityNodeId;

    @Column(name = "component_definition_id", nullable = false)
    private Long componentDefinitionId;

    @Column(name = "instance_name", length = 100)
    private String instanceName;

    @Column(name = "sort_order", nullable = false)
    private Integer sortOrder = 0;

    @Column(name = "props_json", columnDefinition = "TEXT")
    private String propsJson;

    public ComponentInstance() {
    }

    public Long getId() { return id; }
    public Long getActivityNodeId() { return activityNodeId; }
    public void setActivityNodeId(Long activityNodeId) { this.activityNodeId = activityNodeId; }
    public Long getComponentDefinitionId() { return componentDefinitionId; }
    public void setComponentDefinitionId(Long componentDefinitionId) { this.componentDefinitionId = componentDefinitionId; }
    public String getInstanceName() { return instanceName; }
    public void setInstanceName(String instanceName) { this.instanceName = instanceName; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public String getPropsJson() { return propsJson; }
    public void setPropsJson(String propsJson) { this.propsJson = propsJson; }
}
