package com.buyilehu.musicagent.domain.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;
import javax.persistence.Version;

@Entity
@Table(name = "activity_nodes")
public class ActivityNode extends BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "package_id", nullable = false)
    private Long packageId;

    @Column(name = "parent_node_id")
    private Long parentNodeId;

    @Column(nullable = false, length = 120)
    private String title;

    @Column(name = "node_type", nullable = false, length = 50)
    private String nodeType;

    @Column(name = "sort_order", nullable = false)
    private Integer sortOrder = 0;

    @Column(name = "config_json", columnDefinition = "TEXT")
    private String configJson;

    @Version
    @Column(name = "lock_version", nullable = false)
    private Long lockVersion = 0L;

    public ActivityNode() {
    }

    public Long getId() { return id; }
    public Long getPackageId() { return packageId; }
    public void setPackageId(Long packageId) { this.packageId = packageId; }
    public Long getParentNodeId() { return parentNodeId; }
    public void setParentNodeId(Long parentNodeId) { this.parentNodeId = parentNodeId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getNodeType() { return nodeType; }
    public void setNodeType(String nodeType) { this.nodeType = nodeType; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public String getConfigJson() { return configJson; }
    public void setConfigJson(String configJson) { this.configJson = configJson; }
    public Long getLockVersion() { return lockVersion; }
}
