from __future__ import annotations

import json
import os
from typing import Any
import httpx
from app.services.llm_config import llm_runtime_config

from app.services.activity_guidance import infer_activity_type
from app.services.conversation_memory import AgentSession, get_memory
from app.services.model_gateway import ModelGateway
from app.services.music_game_library import detect_template_match_from_text


REACT_SYSTEM_PROMPT = """
你是不亦乐乎-音乐游戏生成智能体的 ReAct 智能体核心。你的任务是通过"思考-行动-观察"循环，把教师的音乐课堂需求转化为高质量的独立网页产物。

## 工作原则
1. 每次响应必须包含明确的 Thought（思考）和 Action（行动）
2. 产物必须是完整的 HTML/CSS/JS 网页，不是配置 JSON
3. 支持多轮迭代：用户说"这里太难"，你要分析并修改
4. 不确定时主动询问，不要猜测

## Action 类型
- UNDERSTAND: 分析用户需求，识别缺失信息
- PLAN: 制定实现计划，拆分成步骤
- GENERATE: 生成完整的 HTML/CSS/JS 代码
- CRITIQUE: 自检代码质量、教学适用性、交互完整性
- FIX: 根据自检结果修复代码
- DELIVER: 确认产物完成，交付给用户
- CLARIFY: 向用户询问缺失的关键信息

## 代码质量标准
1. 必须是单文件 HTML，包含所有 CSS 和 JS
2. 使用中文，面向小学生/初中生
3. 包含完整的交互逻辑，不是静态页面
4. 音乐游戏必须有：开始按钮、游戏规则、操作反馈、得分、重新开始
5. 表现闯关必须有：关卡进度、任务说明、操作区、反馈、下一关
6. 创造拼图必须有：素材区、操作区、试听按钮、保存/分享

## 输出格式
你必须严格按以下格式输出：

Thought: [你的思考过程]

Action: [ACTION_TYPE]
[具体的行动内容，如果是 GENERATE/FIX 则包含完整代码]

如果是 CLARIFY，Action 内容就是你要问用户的问题。
""".strip()


class ReActAgent:
    MAX_INTERNAL_STEPS = 4
    MAX_AUTO_FIXES = 3

    def __init__(self, model_gateway: ModelGateway | None = None):
        self.model = model_gateway or ModelGateway()
        self.memory = get_memory()

    def create_session(self) -> AgentSession:
        return self.memory.create_session()

    def process_message(
        self,
        session_id: str,
        user_message: str,
    ) -> dict[str, Any]:
        session = self.memory.get_session(session_id)
        if not session:
            return {
                "error": "会话不存在，请先创建新会话。",
                "action": "ERROR",
            }

        # 记录用户消息
        session.add_message("user", user_message)
        session.iterations += 1
        session.set_context("auto_fix_attempts", 0)
        self._update_activity_type_from_text(session, user_message)
        template_id = detect_template_match_from_text(user_message)
        if template_id:
            session.set_context("matched_template_id", template_id)
            session.set_context("template_runtime_required", True)
            return self._deliver_template_runtime(session, user_message, template_id)

        # 如果超过最大迭代次数，强制交付
        if session.iterations > session.max_iterations:
            return self._force_deliver(session)

        # 运行 ReAct 循环
        result = self._react_loop(session)
        return result

    def _react_loop(self, session: AgentSession) -> dict[str, Any]:
        try:
            last_thought = ""
            last_action_type = "UNDERSTAND"
            last_observation = ""

            for _ in range(self.MAX_INTERNAL_STEPS):
                # Step 1: Thought - 分析当前状态
                thought = self._generate_thought(session)
                last_thought = thought
                session.add_message("assistant", f"Thought: {thought}", phase="thought")

                # Step 2: Action - 决定行动
                action_result = self._decide_action(session, thought)
                action_type = action_result["type"]
                action_content = action_result["content"]
                last_action_type = action_type

                session.state = action_type.lower()
                session.add_message("assistant", f"Action: {action_type}\n{action_content}", phase="action")

                # Step 3: 执行 Action
                observation = self._execute_action(session, action_type, action_content)
                last_observation = observation
                session.add_message("observation", observation, phase="observation")

                # Step 4: 判断是否需要继续循环
                if action_type == "DELIVER":
                    return self._build_deliver_response(session, action_content)
                elif action_type == "CLARIFY":
                    return self._build_clarify_response(session, action_content)
                elif action_type in ("GENERATE", "FIX"):
                    # 生成/修复后自动进入 CRITIQUE
                    return self._auto_critique_and_continue(session, action_content)
                elif action_type == "CRITIQUE":
                    # 自检后如果有问题，自动 FIX；否则 DELIVER
                    return self._handle_critique_result(session, observation)

                # UNDERSTAND / PLAN 是中间动作；继续同一次请求里的下一拍。
                session.add_message(
                    "observation",
                    f"{action_type} 已完成，请基于该结果继续推进到 CLARIFY、GENERATE 或 DELIVER。",
                    phase="loop_control",
                )

            return self._build_interim_response(session, last_thought, last_action_type, last_observation)
        except RuntimeError as e:
            # LLM 调用失败，回退到本地生成
            return self._fallback_to_local(session, str(e))
        except Exception as e:
            return {
                "action": "ERROR",
                "state": "error",
                "message": f"Agent 执行出错：{e}",
                "error_type": type(e).__name__,
            }

    def _generate_thought(self, session: AgentSession) -> str:
        messages = session.to_llm_messages(REACT_SYSTEM_PROMPT)
        messages.append({
            "role": "user",
            "content": (
                "基于以上对话历史，分析当前状态：\n"
                "1. 用户的核心需求是什么？\n"
                "2. 目前缺少什么信息？\n"
                "3. 下一步应该做什么？\n"
                "请只输出 Thought 内容，不要输出 Action。"
            ),
        })

        response = self._call_llm(messages, temperature=0.3)
        return response.strip()

    def _decide_action(self, session: AgentSession, thought: str) -> dict[str, str]:
        messages = session.to_llm_messages(REACT_SYSTEM_PROMPT)
        messages.append({
            "role": "user",
            "content": (
                f"Thought: {thought}\n\n"
                "根据以上思考，决定下一步 Action。\n"
                "可选 Action 类型：UNDERSTAND, PLAN, GENERATE, CRITIQUE, FIX, DELIVER, CLARIFY\n"
                "请严格按以下格式输出：\n"
                "Action: [TYPE]\n[具体内容]"
            ),
        })

        response = self._call_llm(messages, temperature=0.2)
        return self._parse_action(response)

    def _execute_action(
        self,
        session: AgentSession,
        action_type: str,
        action_content: str,
    ) -> str:
        if action_type == "GENERATE":
            return self._execute_generate(session, action_content)
        elif action_type == "FIX":
            return self._execute_fix(session, action_content)
        elif action_type == "CRITIQUE":
            return self._execute_critique(session, action_content)
        elif action_type in ("UNDERSTAND", "PLAN", "DELIVER", "CLARIFY"):
            return f"Action {action_type} 已记录，等待下一步。"
        else:
            return f"未知 Action 类型: {action_type}"

    def _execute_generate(self, session: AgentSession, code: str) -> str:
        # 提取 HTML 代码
        html_code = self._extract_code_block(code, "html")
        if not html_code:
            html_code = self._extract_raw_html(code)

        if html_code:
            session.set_context("current_html", html_code)
            session.set_context("generation_attempt", session.iterations)
            return f"代码已生成，长度 {len(html_code)} 字符。包含 HTML 结构: {'<!DOCTYPE html>' in html_code}"
        else:
            return "未能从响应中提取有效 HTML 代码。"

    def _execute_fix(self, session: AgentSession, code: str) -> str:
        html_code = self._extract_code_block(code, "html")
        if not html_code:
            html_code = self._extract_raw_html(code)

        if html_code:
            session.set_context("current_html", html_code)
            session.set_context("fix_attempt", session.iterations)
            return f"代码已修复，长度 {len(html_code)} 字符。"
        else:
            return "未能从修复响应中提取有效代码。"

    def _execute_critique(self, session: AgentSession, content: str) -> str:
        html_code = session.get_context("current_html", "")
        if not html_code:
            return "没有可检查的代码。"

        # 运行多个检查
        issues = []

        # 1. 基础结构检查
        if "<!DOCTYPE html>" not in html_code:
            issues.append("缺少 DOCTYPE 声明")
        if "</html>" not in html_code:
            issues.append("HTML 结构不完整")
        if "<script>" not in html_code:
            issues.append("缺少 JavaScript 交互逻辑")

        # 2. 教学适用性检查
        activity_type = session.get_context("activity_type", "")
        if activity_type == "music_game":
            required = ["开始", "规则", "得分", "重新"]
            missing = [w for w in required if w not in html_code]
            if missing:
                issues.append(f"音乐游戏缺少关键元素: {', '.join(missing)}")
        elif activity_type == "performance":
            required = ["关", "任务", "下一关", "反馈"]
            missing = [w for w in required if w not in html_code]
            if missing:
                issues.append(f"表现闯关缺少关键元素: {', '.join(missing)}")

        # 3. 中文检查
        if not any("\u4e00" <= c <= "\u9fff" for c in html_code):
            issues.append("页面缺少中文内容")

        if issues:
            return f"自检发现问题 ({len(issues)} 个): " + "; ".join(issues)
        else:
            return "自检通过：代码结构完整，交互逻辑存在，教学元素齐全。"

    def _auto_critique_and_continue(self, session: AgentSession, code: str) -> dict[str, Any]:
        # 执行自检
        observation = self._execute_critique(session, code)
        session.add_message("observation", observation, phase="auto_critique")

        # 根据自检结果决定下一步
        if "自检通过" in observation:
            # 自检通过，进入 DELIVER
            return self._trigger_deliver(session)
        else:
            # 有问题，触发 FIX
            return self._trigger_fix(session, observation)

    def _handle_critique_result(self, session: AgentSession, observation: str) -> dict[str, Any]:
        if "自检通过" in observation:
            return self._trigger_deliver(session)
        else:
            return self._trigger_fix(session, observation)

    def _trigger_deliver(self, session: AgentSession) -> dict[str, Any]:
        html_code = session.get_context("current_html", "")
        if not html_code:
            # 没有代码，先生成
            return self._build_interim_response(
                session,
                "产物尚未生成，需要先生成代码。",
                "GENERATE",
                "触发代码生成",
            )

        session.state = "delivering"
        session.add_message("assistant", "Action: DELIVER\n产物已完成，准备交付。", phase="action")

        return {
            "action": "DELIVER",
            "state": session.state,
            "iterations": session.iterations,
            "html_code": html_code,
            "message": "产物已生成并通过自检。",
            "next_step": "用户可以继续对话迭代修改，或确认完成。",
        }

    def _trigger_fix(self, session: AgentSession, issues: str) -> dict[str, Any]:
        html_code = session.get_context("current_html", "")
        attempts = int(session.get_context("auto_fix_attempts", 0)) + 1
        session.set_context("auto_fix_attempts", attempts)
        if attempts > self.MAX_AUTO_FIXES:
            session.state = "needs_revision"
            return {
                "action": "ERROR",
                "state": session.state,
                "iterations": session.iterations,
                "html_code": html_code,
                "message": "自动修复已达到上限，产物仍未通过自检。",
                "issues": issues,
                "next_step": "请补充更明确的课堂需求，或稍后重新生成。",
            }

        messages = session.to_llm_messages(REACT_SYSTEM_PROMPT)
        messages.append({
            "role": "user",
            "content": (
                f"当前代码存在以下问题，请修复：\n{issues}\n\n"
                f"当前代码：\n```html\n{html_code[:5000]}\n```\n\n"
                "请输出修复后的完整 HTML 代码。"
            ),
        })

        response = self._call_llm(messages, temperature=0.3)

        # 执行 FIX
        observation = self._execute_fix(session, response)
        session.add_message("observation", observation, phase="fix_execution")

        # FIX 后再次自检
        return self._auto_critique_and_continue(session, response)

    def _fallback_to_local(self, session: AgentSession, error_msg: str) -> dict[str, Any]:
        """当 LLM 不可用时，回退到本地规则生成。"""
        session.state = "fallback"

        # 使用 ModelGateway 的本地生成功能
        need = ""
        for msg in reversed(session.messages):
            if msg.role == "user" and not msg.content.startswith("["):
                need = msg.content
                break

        if not need:
            return {
                "action": "ERROR",
                "state": "error",
                "message": "无法获取用户需求，且 LLM 服务不可用。",
                "error": error_msg,
            }

        try:
            spec, model_info = self.model.generate_tool_spec(need, skills=[], force_local=True)
            from app.services.webpage_generator import render_generated_tool
            from app.services.runtime_paths import get_output_dir

            output_dir = get_output_dir()
            index_path, page_url = render_generated_tool(spec, output_dir)
            html_code = index_path.read_text(encoding="utf-8")

            session.set_context("current_html", html_code)
            session.set_context("activity_type", spec.get("activity_type", ""))

            return {
                "action": "DELIVER",
                "state": "delivering",
                "iterations": session.iterations,
                "html_code": html_code,
                "page_url": page_url,
                "file_path": str(index_path),
                "message": f"LLM 服务暂时不可用，已使用本地规则生成产物。{error_msg}",
                "fallback": True,
                "next_step": "你可以继续对话迭代，或检查网络连接后重试。",
            }
        except Exception as e:
            return {
                "action": "ERROR",
                "state": "error",
                "message": f"LLM 不可用且本地生成也失败：{e}",
                "original_error": error_msg,
            }

    def _force_deliver(self, session: AgentSession) -> dict[str, Any]:
        html_code = session.get_context("current_html", "")
        if not html_code:
            session.state = "needs_input"
            return {
                "action": "ERROR",
                "state": session.state,
                "iterations": session.iterations,
                "message": "已达到最大迭代次数，但当前会话还没有可交付产物。",
                "next_step": "请重置会话后重新发送更具体的课堂需求。",
            }
        return {
            "action": "DELIVER",
            "state": "delivering",
            "iterations": session.iterations,
            "html_code": html_code,
            "message": "已达到最大迭代次数，强制交付当前产物。",
            "warning": "产物可能未完全满足所有要求，建议继续对话优化。",
        }

    def _deliver_template_runtime(self, session: AgentSession, need: str, template_id: str) -> dict[str, Any]:
        session.state = "delivering"
        return {
            "action": "DELIVER",
            "state": session.state,
            "iterations": session.iterations,
            "html_code": "<!DOCTYPE html><html><body>template runtime handoff</body></html>",
            "source_need": need,
            "matched_template_id": template_id,
            "generation_mode": "composed_template_game",
            "message": f"已命中成熟游戏模板 {template_id}，交由新版学生端运行时发布。",
            "next_step": "用户可以打开生成链接试玩新版游戏运行时。",
        }

    def _build_deliver_response(self, session: AgentSession, content: str) -> dict[str, Any]:
        html_code = session.get_context("current_html", "")
        template_id = str(session.get_context("matched_template_id", "") or "")
        return {
            "action": "DELIVER",
            "state": session.state,
            "iterations": session.iterations,
            "html_code": html_code,
            "matched_template_id": template_id,
            "message": content,
            "next_step": "用户可以继续对话迭代修改，或确认完成。",
        }

    def _build_clarify_response(self, session: AgentSession, question: str) -> dict[str, Any]:
        return {
            "action": "CLARIFY",
            "state": session.state,
            "iterations": session.iterations,
            "message": question,
            "next_step": "等待用户回答",
        }

    def _build_interim_response(
        self,
        session: AgentSession,
        thought: str,
        action_type: str,
        observation: str,
    ) -> dict[str, Any]:
        return {
            "action": action_type,
            "state": session.state,
            "iterations": session.iterations,
            "thought": thought,
            "observation": observation,
            "message": f"正在处理：{action_type}。{observation}",
            "next_step": "继续执行下一步",
        }

    def _call_llm(self, messages: list[dict], temperature: float = 0.3) -> str:
        try:
            from openai import APIConnectionError, OpenAI

            llm_config = llm_runtime_config()
            if not llm_config["enabled"]:
                raise RuntimeError("LLM 配置未启用。")
            client = OpenAI(
                api_key=llm_config["api_key"],
                base_url=llm_config["base_url"],
                http_client=httpx.Client(trust_env=False),
            )

            response = client.chat.completions.create(
                model=llm_config["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=8000,
                timeout=60,
            )
            return response.choices[0].message.content or ""
        except ImportError as e:
            raise RuntimeError(f"OpenAI SDK 未安装：{e}") from e
        except APIConnectionError as e:
            raise RuntimeError(f"无法连接到 LLM 服务：{e}") from e
        except Exception as e:
            raise RuntimeError(f"LLM 调用失败：{e}") from e

    def _parse_action(self, response: str) -> dict[str, str]:
        lines = response.strip().split("\n")
        action_type = "UNDERSTAND"
        content = response

        for i, line in enumerate(lines):
            if line.startswith("Action:"):
                action_line = line.replace("Action:", "").strip()
                # 提取类型
                for possible_type in ["UNDERSTAND", "PLAN", "GENERATE", "CRITIQUE", "FIX", "DELIVER", "CLARIFY"]:
                    if possible_type in action_line.upper():
                        action_type = possible_type
                        break
                # 内容在下一行开始
                content = "\n".join(lines[i + 1:]).strip()
                break

        return {"type": action_type, "content": content}

    def _extract_code_block(self, text: str, lang: str) -> str:
        import re
        pattern = rf"```{lang}\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_raw_html(self, text: str) -> str:
        # 如果没有代码块，尝试提取 HTML 标签
        if "<!DOCTYPE html>" in text or "<html>" in text:
            start = text.find("<!DOCTYPE html>")
            if start == -1:
                start = text.find("<html>")
            if start != -1:
                return text[start:].strip()
        return ""

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        session = self.memory.get_session(session_id)
        if not session:
            return {"error": "会话不存在"}
        return {
            "session_id": session_id,
            "state": session.state,
            "iterations": session.iterations,
            "message_count": len(session.messages),
            "has_artifact": bool(session.get_context("current_html")),
            "context": {
                k: v for k, v in session.context.items()
                if k != "current_html"  # 不返回完整代码
            },
        }

    def reset_session(self, session_id: str) -> dict[str, Any]:
        session = self.memory.get_session(session_id)
        if not session:
            return {"error": "会话不存在"}

        session.state = "idle"
        session.iterations = 0
        session.current_artifact = {}
        session.context = {}
        # 保留最近的对话历史，但标记为已重置
        session.add_message("system", "会话已重置，开始新的生成任务。")

        return {
            "session_id": session_id,
            "state": session.state,
            "message": "会话已重置，可以开始新的对话。",
        }

    def iterate_on_artifact(
        self,
        session_id: str,
        feedback: str,
    ) -> dict[str, Any]:
        session = self.memory.get_session(session_id)
        if not session:
            return {"error": "会话不存在"}

        html_code = session.get_context("current_html", "")
        if not html_code:
            return {
                "error": "当前会话没有产物，无法迭代。",
                "action": "ERROR",
            }

        # 记录用户反馈
        session.add_message("user", f"[迭代反馈] {feedback}")
        session.set_context("auto_fix_attempts", 0)
        self._update_activity_type_from_text(session, feedback)

        # 直接触发 FIX 流程
        return self._trigger_fix(session, f"用户反馈: {feedback}")

    def _update_activity_type_from_text(self, session: AgentSession, text: str) -> None:
        inferred = infer_activity_type(text)
        if inferred != "unknown":
            session.set_context("activity_type", inferred)
