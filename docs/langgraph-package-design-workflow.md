# LangGraph 互动包设计工作流

## 接入位置

LangGraph 位于 Python 能力服务的互动包设计边界：

```text
Java GenerationJobService
  -> PythonCapabilityClient
  -> POST /api/v1/packages/design
  -> LangGraph package design workflow
  -> ActivityChain
```

现有 HTTP 接口、请求参数以及 `package-design.v1` 响应结构保持兼容。Java 服务不需要改变调用方式。

## 工作流节点

```text
START
  -> prepare
  -> call_model
      -> validate -> finalize -> END
      -> call_model (切换下一个模型提供商)
      -> fallback -> finalize -> END
```

- `prepare`：读取华东师大模型和豆包模型配置，初始化执行状态。
- `call_model`：通过 `package_design_model` 工具调用当前模型。
- `validate`：通过 `validate_package_design` 工具校验活动数量、白名单 ID 和节点结构。
- `fallback`：模型不可用或结果全部不合格时，通过 `rule_package_design` 工具生成确定性方案。
- `finalize`：输出兼容结果，并写入 trace ID、节点轨迹和工具调用记录。

## 路由与降级

模型提供商顺序保持为：

1. `chat_ecnu`
2. `doubao`
3. `rule_fallback`

模型请求异常和结构校验失败都会进入下一个提供商。所有失败原因会写入 `design.fallback_reason`，不会把 API Key 写入返回结果。

## 可观测字段

`POST /api/v1/packages/design` 的 `data.design` 新增：

- `workflow_engine`：固定为 `langgraph`。
- `workflow_steps`：本次请求实际经过的节点与分支。
- `tool_calls`：本次请求调用过的工具名称。
- `trace_id`：单次工作流执行标识。

## 本地验证

```powershell
cd backend\python-capability-library
.\.venv\Scripts\python.exe -m unittest tests.test_api
```
