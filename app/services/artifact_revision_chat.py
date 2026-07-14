from __future__ import annotations

from copy import deepcopy
import json
import re
from dataclasses import dataclass, field
from time import time
from typing import Any
from uuid import uuid4

from app.services.llm_config import llm_runtime_config
from app.services.model_gateway import ModelGateway, _json_from_text
from app.services.game_workflow_orchestrator import build_direct_game_workflow, build_lesson_game_workflow
from app.services.template_patch_command import build_patch_command


REVISION_CHAT_SYSTEM_PROMPT = """
你是不亦乐乎-音乐游戏生成智能体的产物修改对话助手。
你的职责不是直接改代码，而是先理解教师对“当前已生成网页”的修改意图，再生成一份稳定、可执行的修改说明，交给后续 OpenCode 执行。

你必须遵守：
1. 你面对的是“已经生成好的当前网页”，不是从头重新生成。
2. 优先保留当前教案目标、曲目、学段、核心音乐概念和原活动结构。
3. 如果用户表达模糊，要指出你当前理解的修改方向，并给出是否需要确认。
4. 如果用户在提问、犹豫或讨论，不要默认执行修改。
5. 不要新增用户没有要求的大功能。
6. 如果涉及音乐逻辑、歌曲片段、音高答案、节奏答案等，必须提示保持现有音乐逻辑契约，不自行发明新答案。
7. 如果用户使用“这块、上面那个、标题、首页、我的作品、导航、校徽、首屏、卡片”等指代词，你要主动把它映射到具体页面区域，再生成修改说明。
8. 如果用户意图已经很明确，不要只说“我理解了”，而要明确指出你认为要改的是哪一块、改成什么方向、哪些内容保持不动。

请只输出 JSON 对象，字段如下：
{
  "reply": "给用户看的中文回复，简洁说明你的理解",
  "intent": "revise_artifact | ask_clarification | discuss_only",
  "needs_confirmation": true,
  "should_apply_directly": false,
  "revision_instruction": "交给 OpenCode 的明确修改说明",
  "preserve": ["必须保留项"],
  "scope": ["本次修改涉及的范围"],
  "risks": ["风险或需要注意的点"],
  "clarifying_question": "如果需要追问，这里写问题，否则为空字符串"
}
""".strip()


@dataclass
class RevisionChatMessage:
    role: str
    content: str
    timestamp: float = field(default_factory=time)


@dataclass
class ArtifactRevisionSession:
    session_id: str
    current_spec: str
    current_file_path: str
    current_page_url: str
    summary: dict[str, Any]
    model_info: dict[str, Any] = field(default_factory=dict)
    pending_revision_instruction: str = ""
    pending_user_message: str = ""
    pending_template_switch_proposal: dict[str, Any] = field(default_factory=dict)
    pending_template_switch_candidate: dict[str, Any] = field(default_factory=dict)
    messages: list[RevisionChatMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time)
    updated_at: float = field(default_factory=time)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(RevisionChatMessage(role=role, content=content))
        self.updated_at = time()

    def recent_history_text(self, limit: int = 8) -> str:
        lines: list[str] = []
        for item in self.messages[-limit:]:
            speaker = "老师" if item.role == "user" else "助手"
            lines.append(f"{speaker}：{item.content}")
        return "\n".join(lines)


class ArtifactRevisionChatService:
    def __init__(self, model_gateway: ModelGateway | None = None) -> None:
        self.model_gateway = model_gateway or ModelGateway()
        self._sessions: dict[str, ArtifactRevisionSession] = {}

    def create_session(
        self,
        *,
        current_spec: str,
        current_file_path: str,
        current_page_url: str,
    ) -> ArtifactRevisionSession:
        spec_payload = self._parse_spec(current_spec)
        session = ArtifactRevisionSession(
            session_id=uuid4().hex[:12],
            current_spec=current_spec,
            current_file_path=current_file_path,
            current_page_url=current_page_url,
            summary=self._artifact_summary(spec_payload),
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> ArtifactRevisionSession | None:
        return self._sessions.get(session_id)

    def analyze_message(self, session_id: str, user_message: str) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise ValueError("修改会话不存在，请重新打开作品后再试。")

        user_message = (user_message or "").strip()
        if not user_message:
            raise ValueError("请先输入你想修改的内容。")

        session.add_message("user", user_message)
        commit_payload = self._template_switch_commit_payload(session, user_message)
        candidate_payload = self._template_switch_candidate_payload(session, user_message) if not commit_payload else {}
        switch_payload = self._template_switch_proposal_payload(session, user_message) if not commit_payload and not candidate_payload else {}
        capability_payload = (
            self._capability_feedback_proposal_payload(session, user_message)
            if not commit_payload and not candidate_payload and not switch_payload
            else {}
        )
        if commit_payload:
            payload, model_info = commit_payload, {"provider": "local", "model": "template-switch-commit"}
        elif candidate_payload:
            payload, model_info = candidate_payload, {"provider": "local", "model": "template-switch-candidate"}
        elif switch_payload:
            payload, model_info = switch_payload, {"provider": "local", "model": "template-switch-proposal"}
        elif capability_payload:
            payload, model_info = capability_payload, {"provider": "local", "model": "capability-feedback-proposal"}
        else:
            payload, model_info = self._analyze_with_model(session, user_message)
        session.model_info = model_info
        session.pending_user_message = user_message
        session.pending_revision_instruction = payload.get("revision_instruction", "").strip()
        if isinstance(payload.get("template_switch_proposal"), dict):
            session.pending_template_switch_proposal = deepcopy(payload["template_switch_proposal"])
        elif isinstance(payload.get("template_switch_candidate"), dict):
            session.pending_template_switch_candidate = deepcopy(payload["template_switch_candidate"])
            proposal = payload["template_switch_candidate"].get("proposal", {})
            session.pending_template_switch_proposal = deepcopy(proposal) if isinstance(proposal, dict) else {}
        elif isinstance(payload.get("template_switch_commit"), dict):
            session.pending_template_switch_candidate = {}
            session.pending_template_switch_proposal = {}
        session.add_message("assistant", payload.get("reply", ""))
        return {
            "session_id": session.session_id,
            "analysis": payload,
            "model": model_info,
            "history": self._public_history(session),
        }

    def apply_pending_revision(self, session_id: str) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise ValueError("修改会话不存在，请重新打开作品后再试。")
        if not session.pending_revision_instruction.strip():
            raise ValueError("当前没有可执行的修改说明，请先对话确认要修改什么。")
        return {
            "current_spec": session.current_spec,
            "current_file_path": session.current_file_path,
            "current_page_url": session.current_page_url,
            "revision": session.pending_revision_instruction,
            "source_message": session.pending_user_message,
        }

    def update_after_revision(self, session_id: str, result: dict[str, Any]) -> None:
        session = self.get_session(session_id)
        if session is None:
            return
        spec_payload = result.get("spec", {})
        feedback = patch_feedback_from_revision_result(result)
        session.current_spec = json.dumps(spec_payload, ensure_ascii=False)
        session.current_file_path = result.get("file_path", session.current_file_path)
        session.current_page_url = result.get("page_url", session.current_page_url)
        session.summary = self._artifact_summary(spec_payload)
        session.pending_revision_instruction = ""
        session.pending_user_message = ""
        if feedback:
            session.summary["patch_feedback"] = feedback
        session.add_message("assistant", feedback.get("teacher_message") if feedback else "修改已应用到当前作品。")

    def _analyze_with_model(self, session: ArtifactRevisionSession, user_message: str) -> tuple[dict[str, Any], dict[str, Any]]:
        prompt = self._build_analysis_prompt(session, user_message)
        llm_config = llm_runtime_config()
        if llm_config["enabled"]:
            try:
                content = self.model_gateway._chat_with_openai_compatible(prompt)
                payload = self._normalize_analysis_payload(_json_from_text(content), session, user_message)
                return payload, {"provider": llm_config["provider"], "model": llm_config["model"]}
            except Exception as exc:
                payload = self._local_analysis(session, user_message)
                return payload, {
                    "provider": "local_fallback",
                    "model": "rule-based-revision-analyzer",
                    "error": str(exc),
                }
        payload = self._local_analysis(session, user_message)
        return payload, {"provider": "local_fallback", "model": "rule-based-revision-analyzer"}

    def _build_analysis_prompt(self, session: ArtifactRevisionSession, user_message: str) -> str:
        spec_summary = json.dumps(session.summary, ensure_ascii=False)
        return "\n".join(
            [
                REVISION_CHAT_SYSTEM_PROMPT,
                "",
                f"当前产物摘要：{spec_summary}",
                f"当前页面结构线索：{self._ui_context_hint(session)}",
                f"当前页面路径：{session.current_file_path or session.current_page_url or 'unknown'}",
                "最近对话：",
                session.recent_history_text() or "无",
                "",
                f"老师新消息：{user_message}",
            ]
        )

    def _template_switch_proposal_payload(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        feedback = session.summary.get("patch_feedback") if isinstance(session.summary.get("patch_feedback"), dict) else {}
        recommended = str(feedback.get("recommended_template_id") or "").strip()
        if not recommended or not self._confirms_template_switch(user_message):
            return {}
        workflow = session.summary.get("template_workflow") if isinstance(session.summary.get("template_workflow"), dict) else {}
        instance = workflow.get("instance") if isinstance(workflow.get("instance"), dict) else {}
        config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
        proposal = {
            "proposal_type": "template_switch_proposal",
            "from_template_id": str(instance.get("template_id") or config.get("template_id") or ""),
            "to_template_id": recommended,
            "reason": feedback.get("reason", ""),
            "source_teacher_message": feedback.get("teacher_message", ""),
            "preserve": session.summary.get("preserve_defaults", []),
            "requires_teacher_confirmation": True,
            "requires_full_regeneration": False,
            "status": "needs_teacher_confirmation",
        }
        return {
            "reply": f"我先记录一个切换玩法提案：从 {proposal['from_template_id']} 切到 {recommended}。确认前不会改动当前游戏。",
            "intent": "propose_template_switch",
            "needs_confirmation": True,
            "should_apply_directly": False,
            "revision_instruction": "",
            "template_switch_proposal": proposal,
            "preserve": session.summary.get("preserve_defaults", []),
            "scope": ["template_switch_proposal"],
            "risks": ["切换模板会改变玩法底盘，必须二次确认后再执行。"],
            "clarifying_question": "确认要切换到这个推荐玩法吗？",
        }

    def _capability_feedback_proposal_payload(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        feedback = session.summary.get("patch_feedback") if isinstance(session.summary.get("patch_feedback"), dict) else {}
        recommended = str(feedback.get("recommended_template_id") or "").strip()
        teacher_message = str(feedback.get("teacher_message") or "").strip()
        if not recommended or not teacher_message or not self._requests_unsupported_music_goal(user_message, feedback):
            return {}
        workflow = session.summary.get("template_workflow") if isinstance(session.summary.get("template_workflow"), dict) else {}
        instance = workflow.get("instance") if isinstance(workflow.get("instance"), dict) else {}
        config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
        proposal = {
            "proposal_type": "template_switch_proposal",
            "from_template_id": str(instance.get("template_id") or config.get("template_id") or ""),
            "to_template_id": recommended,
            "reason": feedback.get("reason", ""),
            "source_teacher_message": teacher_message,
            "preserve": session.summary.get("preserve_defaults", []),
            "requires_teacher_confirmation": True,
            "requires_full_regeneration": False,
            "status": "needs_teacher_confirmation",
        }
        return {
            "reply": teacher_message,
            "intent": "propose_template_switch",
            "needs_confirmation": True,
            "should_apply_directly": False,
            "revision_instruction": "",
            "template_switch_proposal": proposal,
            "preserve": session.summary.get("preserve_defaults", []),
            "scope": ["template_switch_proposal"],
            "risks": ["当前玩法不能直接承接这个音乐目标，需要先确认是否切换玩法。"],
            "clarifying_question": "要按这个建议生成候选玩法版本吗？",
        }

    def _template_switch_candidate_payload(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        proposal = session.pending_template_switch_proposal
        if not proposal or not self._confirms_pending_template_switch(user_message):
            return {}
        candidate_workflow = self._build_template_switch_candidate_workflow(session, proposal)
        if not candidate_workflow:
            return {}
        original_workflow = session.summary.get("template_workflow") if isinstance(session.summary.get("template_workflow"), dict) else {}
        ready_proposal = {**deepcopy(proposal), "status": "candidate_ready"}
        return {
            "reply": "我已生成一个候选玩法版本；当前游戏仍保持不变，等你选择是否应用候选版本。",
            "intent": "prepare_template_switch_candidate",
            "needs_confirmation": True,
            "should_apply_directly": False,
            "revision_instruction": "",
            "template_switch_candidate": {
                "proposal": ready_proposal,
                "original_workflow": deepcopy(original_workflow),
                "candidate_workflow": candidate_workflow,
                "preserves_original_workflow": True,
                "requires_teacher_selection": True,
                "application_mode": "candidate_only",
            },
            "preserve": proposal.get("preserve", []),
            "scope": ["template_switch_candidate"],
            "risks": ["候选版本只用于比较，不能自动覆盖当前模板实例。"],
            "clarifying_question": "是否应用这个候选玩法版本？",
        }

    def _template_switch_commit_payload(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        candidate = (
            session.pending_template_switch_candidate
            if isinstance(session.pending_template_switch_candidate, dict)
            else {}
        )
        if not candidate or not self._confirms_apply_template_switch(user_message):
            return {}
        previous_workflow = candidate.get("original_workflow") if isinstance(candidate.get("original_workflow"), dict) else {}
        current_workflow = candidate.get("candidate_workflow") if isinstance(candidate.get("candidate_workflow"), dict) else {}
        if not previous_workflow or not current_workflow:
            return {}
        proposal = candidate.get("proposal") if isinstance(candidate.get("proposal"), dict) else {}
        from_template_id = str(
            proposal.get("from_template_id")
            or (previous_workflow.get("instance") or {}).get("template_id")
            or ""
        )
        to_template_id = str(
            proposal.get("to_template_id")
            or (current_workflow.get("instance") or {}).get("template_id")
            or ""
        )
        updated_spec = self._template_switch_updated_spec(
            session=session,
            previous_workflow=previous_workflow,
            current_workflow=current_workflow,
            from_template_id=from_template_id,
            to_template_id=to_template_id,
            source_message=user_message,
        )
        session.current_spec = json.dumps(updated_spec, ensure_ascii=False)
        session.summary = self._artifact_summary(updated_spec)
        return {
            "reply": "已将候选玩法提交为当前新版本，并保留了切换前的旧版本记录。",
            "intent": "commit_template_switch_candidate",
            "needs_confirmation": False,
            "should_apply_directly": True,
            "revision_instruction": "",
            "template_switch_commit": {
                "commit_type": "template_switch_candidate_commit",
                "status": "committed",
                "from_template_id": from_template_id,
                "to_template_id": to_template_id,
                "previous_workflow": deepcopy(previous_workflow),
                "current_workflow": deepcopy(current_workflow),
                "updated_spec": deepcopy(updated_spec),
                "requires_full_regeneration": False,
                "application_mode": "workflow_contract_replace",
            },
            "preserve": proposal.get("preserve", []) if isinstance(proposal.get("preserve"), list) else [],
            "scope": ["template_switch_commit"],
            "risks": [],
            "clarifying_question": "",
        }

    def _template_switch_updated_spec(
        self,
        *,
        session: ArtifactRevisionSession,
        previous_workflow: dict[str, Any],
        current_workflow: dict[str, Any],
        from_template_id: str,
        to_template_id: str,
        source_message: str,
    ) -> dict[str, Any]:
        spec_payload = self._parse_spec(session.current_spec)
        updated = deepcopy(spec_payload) if spec_payload else {}
        updated["generation_mode"] = updated.get("generation_mode") or "composed_template_game"
        updated["template_workflow"] = deepcopy(current_workflow)
        self._sync_template_workflow_fields(updated, current_workflow)
        commits = updated.get("template_switch_commits") if isinstance(updated.get("template_switch_commits"), list) else []
        commits.append(
            {
                "commit_type": "template_switch_candidate_commit",
                "status": "committed",
                "from_template_id": from_template_id,
                "to_template_id": to_template_id,
                "source_message": source_message,
                "previous_workflow": deepcopy(previous_workflow),
                "current_workflow": deepcopy(current_workflow),
                "requires_full_regeneration": False,
                "application_mode": "workflow_contract_replace",
            }
        )
        updated["template_switch_commits"] = commits
        return updated

    def _sync_template_workflow_fields(self, spec_payload: dict[str, Any], workflow: dict[str, Any]) -> None:
        instance = workflow.get("instance") if isinstance(workflow.get("instance"), dict) else {}
        config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
        spec_payload["template_instance"] = deepcopy(instance)
        spec_payload["template_config"] = deepcopy(config)
        spec_payload["matched_template_id"] = instance.get("template_id", "")
        for key in (
            "lesson_adaptation",
            "template_decision",
            "gameplay_blueprint",
            "experience_script",
            "theme_pack",
            "presentation_pack",
            "opencode_role_policy",
            "render_spec",
            "frontend_handoff_contract",
            "responsibility_map",
            "game_variant_spec",
            "template_instance_patch",
        ):
            if key in workflow:
                spec_payload[key] = deepcopy(workflow.get(key))
        music_game = spec_payload.get("music_game") if isinstance(spec_payload.get("music_game"), dict) else {}
        music_game = deepcopy(music_game)
        music_game["template_id"] = instance.get("template_id", "")
        music_game["matched_template_id"] = instance.get("template_id", "")
        music_game["template_label"] = instance.get("template_label", "")
        music_game["template_config"] = deepcopy(config)
        music_game["template_skin"] = deepcopy(instance.get("skin", {}))
        music_game["template_student_task"] = deepcopy(instance.get("student_task", {}))
        spec_payload["music_game"] = music_game

    def _build_template_switch_candidate_workflow(
        self,
        session: ArtifactRevisionSession,
        proposal: dict[str, Any],
    ) -> dict[str, Any]:
        workflow = session.summary.get("template_workflow") if isinstance(session.summary.get("template_workflow"), dict) else {}
        target_template_id = str(proposal.get("to_template_id") or "").strip()
        if not workflow or not target_template_id:
            return {}
        source = workflow.get("source") if isinstance(workflow.get("source"), dict) else {}
        options = deepcopy(source.get("options")) if isinstance(source.get("options"), dict) else {}
        options["template_id"] = target_template_id
        workflow_kind = str(workflow.get("workflow_kind") or "").strip()
        if workflow_kind == "lesson_game":
            lesson_proposal = {
                "lesson_context": deepcopy(source.get("lesson_context", {})),
                "lesson_source": deepcopy(source.get("lesson_source", {})),
                "lesson_fit": deepcopy(source.get("lesson_fit", {})),
                "lesson_adaptation": deepcopy(source.get("lesson_adaptation", {})),
                "music_element_adjustment_contract": deepcopy(source.get("music_element_adjustment_contract", {})),
                "need": str(session.summary.get("original_user_need") or ""),
            }
            candidate = build_lesson_game_workflow(lesson_proposal, options)
        else:
            need = str(source.get("need") or session.summary.get("original_user_need") or "").strip()
            candidate = build_direct_game_workflow(need, options)
        candidate["template_switch_context"] = {
            "proposal_type": "template_switch_candidate",
            "from_template_id": proposal.get("from_template_id", ""),
            "to_template_id": target_template_id,
            "reason": proposal.get("reason", ""),
            "source_teacher_message": proposal.get("source_teacher_message", ""),
            "status": "candidate_ready",
            "application_mode": "candidate_only",
        }
        return candidate

    def _confirms_pending_template_switch(self, user_message: str) -> bool:
        text = str(user_message or "").strip()
        if not text:
            return False
        if self._confirms_template_switch(text):
            return True
        return any(word in text for word in ("确认", "可以", "同意", "生成候选", "候选版本", "应用候选"))

    def _confirms_apply_template_switch(self, user_message: str) -> bool:
        text = str(user_message or "").strip()
        if not text:
            return False
        return any(word in text for word in ("应用候选", "应用这个候选", "采用候选", "使用候选", "就用候选", "替换当前", "提交候选"))

    def _confirms_template_switch(self, user_message: str) -> bool:
        text = str(user_message or "").strip()
        if not text:
            return False
        confirm_words = ("好", "可以", "确认", "同意", "就", "切到", "换成", "改用", "用这个", "这个玩法")
        return any(word in text for word in confirm_words) and any(word in text for word in ("切", "换", "改用", "玩法", "这个"))

    def _requests_unsupported_music_goal(self, user_message: str, feedback: dict[str, Any]) -> bool:
        text = str(user_message or "").strip()
        if not text:
            return False
        if not any(word in text for word in ("改", "换", "调整", "变成", "做成", "音色", "节奏", "曲式", "唱名", "音高")):
            return False
        teacher_message = str(feedback.get("teacher_message") or "")
        if "音色" in teacher_message and "音色" in text:
            return True
        if "节奏" in teacher_message and "节奏" in text:
            return True
        if "曲式" in teacher_message and "曲式" in text:
            return True
        if "唱名" in teacher_message and "唱名" in text:
            return True
        if "音高" in teacher_message and "音高" in text:
            return True
        return any(word in text for word in ("那就", "就按", "按这个", "这个建议", "比较", "听辨"))

    def _normalize_analysis_payload(self, payload: dict[str, Any], session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        preserve = payload.get("preserve")
        scope = payload.get("scope")
        risks = payload.get("risks")
        area_hints = self._detect_area_hints(user_message)
        normalized = {
            "reply": str(payload.get("reply", "我已经理解了这次修改方向。")).strip() or "我已经理解了这次修改方向。",
            "intent": str(payload.get("intent", "ask_clarification")).strip() or "ask_clarification",
            "needs_confirmation": bool(payload.get("needs_confirmation", True)),
            "should_apply_directly": bool(payload.get("should_apply_directly", False)),
            "revision_instruction": str(payload.get("revision_instruction", "")).strip(),
            "preserve": preserve if isinstance(preserve, list) else [],
            "scope": scope if isinstance(scope, list) else [],
            "risks": risks if isinstance(risks, list) else [],
            "clarifying_question": str(payload.get("clarifying_question", "")).strip(),
        }
        if not normalized["preserve"]:
            normalized["preserve"] = session.summary.get("preserve_defaults", [])
        if self._is_generic_revision_reply(normalized["reply"]):
            normalized["reply"] = self._build_local_reply(area_hints, user_message)
        if normalized["intent"] == "revise_artifact" and not normalized["clarifying_question"] and self._looks_spatially_ambiguous(user_message):
            normalized["clarifying_question"] = self._default_clarifying_question(area_hints)
        if normalized["intent"] == "revise_artifact" and normalized["revision_instruction"]:
            normalized["revision_instruction"] = self._enrich_revision_instruction(
                normalized["revision_instruction"],
                area_hints=area_hints,
                preserve=normalized["preserve"],
            )
        if normalized["intent"] == "revise_artifact":
            normalized["patch_command"] = self._build_patch_command_for_session(session, user_message)
        if normalized["intent"] == "revise_artifact" and self._references_previous_version(user_message, session):
            normalized = self._clarify_previous_version_reference(normalized)
        return normalized

    def _local_analysis(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        lowered = user_message.lower()
        discuss_only = any(keyword in user_message for keyword in ["能不能", "可以吗", "怎么", "为什么", "是否"]) and not any(
            keyword in user_message for keyword in ["改", "调整", "增加", "删", "删除", "修改", "换成"]
        )
        if discuss_only:
            return {
                "reply": "这更像是在讨论方案。我可以先帮你整理成修改方向，确认后再真正改当前网页。",
                "intent": "discuss_only",
                "needs_confirmation": True,
                "should_apply_directly": False,
                "revision_instruction": "",
                "preserve": session.summary.get("preserve_defaults", []),
                "scope": ["discussion"],
                "risks": [],
                "clarifying_question": "你希望我直接把它改进当前网页，还是先只讨论方案？",
            }

        scope: list[str] = []
        area_hints = self._detect_area_hints(user_message)
        if any(token in user_message for token in ["规则", "玩法", "关卡"]):
            scope.append("game_rules")
        if any(token in user_message for token in ["按钮", "界面", "颜色", "布局", "字", "文案"]):
            scope.append("ui")
        if any(token in user_message for token in ["标题", "字标", "字体", "校徽", "logo", "导航", "首页", "首屏", "卡片", "头部", "上面"]):
            scope.append("layout_region")
        if any(token in user_message for token in ["简单", "难", "低年级", "一年级", "二年级"]):
            scope.append("difficulty")
        if any(token in user_message for token in ["音乐", "音高", "节奏", "旋律", "sol", "mi"]):
            scope.append("music_logic")
        if not scope:
            scope.append("targeted_adjustment")

        preserve = session.summary.get("preserve_defaults", [])
        area_text = f"你认为对应区域是：{'、'.join(area_hints)}。" if area_hints else ""
        instruction = (
            "请基于当前已生成网页做增量修改，不要重做整页。"
            f"本次用户要求：{user_message}。"
            f"{area_text}"
            f"必须保留：{'、'.join(preserve) if preserve else '当前教案目标和活动结构'}。"
            "只修改用户明确提到的部分。"
        )
        risks: list[str] = []
        if "music_logic" in scope:
            risks.append("涉及音乐逻辑时必须继续遵守现有 music-logic-contract 和歌曲材料约束。")
        if area_hints and any("首页头部" in item or "首屏" in item for item in area_hints):
            risks.append("涉及首页头部时，优先调整尺寸、间距和清晰度，不要顺手改动生成链路或作品内容。")

        previous_version_reference = self._references_previous_version(user_message, session)

        return {
            "reply": (
                "我理解为：借鉴旧版本表现，但仍修改当前新版本；旧版本只作为参考，不会切回去。"
                if previous_version_reference
                else self._build_local_reply(area_hints, user_message)
            ),
            "intent": "revise_artifact",
            "needs_confirmation": True,
            "should_apply_directly": False,
            "revision_instruction": (
                f"{instruction}老师提到旧版本时，只借鉴旧版本表现，但仍修改当前新版本；不要把旧版本 URL 或旧玩法作为执行对象。"
                if previous_version_reference
                else instruction
            ),
            "patch_command": self._build_patch_command_for_session(session, user_message),
            "preserve": preserve,
            "scope": scope,
            "risks": risks,
            "clarifying_question": "",
        }

    def _artifact_summary(self, spec_payload: dict[str, Any]) -> dict[str, Any]:
        activity_type = str(spec_payload.get("activity_type", "mixed"))
        song_name = str(spec_payload.get("song_name", "自选歌曲"))
        grade_band = str(spec_payload.get("grade_band", "小学"))
        title = str(spec_payload.get("title", "音乐课堂工具"))
        subtitle = str(spec_payload.get("subtitle", ""))
        original_need = str(spec_payload.get("original_user_need", ""))
        must_keep = [title, song_name, grade_band]
        if activity_type:
            must_keep.append(activity_type)
        if "sol" in original_need.lower() or "mi" in original_need.lower():
            must_keep.extend(["sol", "mi"])
        summary = {
            "activity_type": activity_type,
            "title": title,
            "subtitle": subtitle,
            "song_name": song_name,
            "grade_band": grade_band,
            "original_user_need": original_need[:500],
            "template_workflow": spec_payload.get("template_workflow", {}) if isinstance(spec_payload.get("template_workflow"), dict) else {},
            "template_switch_delivery": (
                spec_payload.get("template_switch_delivery", {})
                if isinstance(spec_payload.get("template_switch_delivery"), dict)
                else {}
            ),
            "preserve_defaults": [item for item in must_keep if item],
        }
        feedback = patch_feedback_from_spec(spec_payload)
        if feedback:
            summary["patch_feedback"] = feedback
        return summary

    def _build_patch_command_for_session(self, session: ArtifactRevisionSession, user_message: str) -> dict[str, Any]:
        workflow = session.summary.get("template_workflow")
        if not isinstance(workflow, dict) or not workflow:
            return {}
        return build_patch_command(workflow, user_message)

    def _ui_context_hint(self, session: ArtifactRevisionSession) -> str:
        activity_type = str(session.summary.get("activity_type") or "mixed")
        title = str(session.summary.get("title") or "音乐课堂工具")
        hints = [
            "首页包含顶部头部区，里面有主标题、不亦乐乎字标、校徽 logo、导航。",
            "首页包含首屏入口卡片，如教案生成、直接生成、我的作品。",
            "作品卡里包含预览、继续修改、对话修改、一键升级等区域。",
            f"当前作品标题是：{title}。",
            f"当前活动类型是：{activity_type}。",
        ]
        return " ".join(hints)

    def _detect_area_hints(self, user_message: str) -> list[str]:
        text = str(user_message or "")
        hints: list[str] = []
        mapping = [
            (r"(校徽|logo)", "右上角校徽 logo"),
            (r"(导航|首页|教案生成|直接生成|我的作品)", "顶部导航区"),
            (r"(标题|字标|字体|不亦乐乎)", "顶部主标题字标区"),
            (r"(头部|上面|最上面|首屏)", "首页头部/首屏区域"),
            (r"(卡片|模块|这块)", "首页入口卡片区域"),
            (r"(我的作品)", "我的作品入口或作品卡区域"),
        ]
        for pattern, label in mapping:
            if re.search(pattern, text, re.IGNORECASE) and label not in hints:
                hints.append(label)
        return hints

    def _build_local_reply(self, area_hints: list[str], user_message: str) -> str:
        if area_hints:
            return (
                f"我理解为：你这次主要想改 {'、'.join(area_hints)}，"
                "在保留当前教学目标和生成逻辑不变的前提下，只调整你刚才提到的那部分。"
            )
        return "我理解为：在保留当前教学目标和结构的前提下，只修改你刚才提到的部分。确认后我会基于当前网页继续改。"

    def _is_generic_revision_reply(self, reply: str) -> bool:
        text = str(reply or "").strip()
        generic_markers = [
            "我理解为：在保留当前教学目标和结构的前提下，只修改你刚才提到的部分。",
            "确认后我会基于当前网页继续改。",
            "我已经理解了这次修改方向。",
        ]
        return any(marker in text for marker in generic_markers)

    def _looks_spatially_ambiguous(self, user_message: str) -> bool:
        text = str(user_message or "").strip()
        if not text:
            return False
        spatial_words = ["这块", "这一块", "上面", "下面", "这里", "那里", "这个", "那个"]
        anchor_words = ["标题", "字标", "校徽", "logo", "导航", "首页", "首屏", "卡片", "我的作品", "按钮", "文案"]
        return any(word in text for word in spatial_words) and not any(word in text for word in anchor_words)

    def _default_clarifying_question(self, area_hints: list[str]) -> str:
        if area_hints:
            return f"我先按 {'、'.join(area_hints)} 理解；如果你指的不是这块，可以再说一下具体位置。"
        return "我可以继续改，但你这句里位置指代还有点泛。你可以补一句是首页头部、标题区、校徽区，还是作品卡那一块。"

    def _enrich_revision_instruction(self, instruction: str, *, area_hints: list[str], preserve: list[str]) -> str:
        parts = [instruction.strip()]
        if area_hints:
            parts.append(f"优先按以下页面区域理解并修改：{'、'.join(area_hints)}。")
        if preserve:
            parts.append(f"继续保留这些核心内容不变：{'、'.join(str(item).strip() for item in preserve if str(item).strip())}。")
        parts.append("如果用户是在说尺寸、模糊、留白、位置，请优先调整该区域的字号、描边、清晰度、间距、尺寸和布局，不要泛化成整页重做。")
        return "".join(parts)

    def _references_previous_version(self, user_message: str, session: ArtifactRevisionSession) -> bool:
        text = str(user_message or "").strip()
        if not text or not any(word in text for word in ("旧版本", "旧版", "上一版", "之前版本", "原来版本")):
            return False
        delivery = session.summary.get("template_switch_delivery")
        return isinstance(delivery, dict) and str(delivery.get("status") or "") == "published"

    def _clarify_previous_version_reference(self, payload: dict[str, Any]) -> dict[str, Any]:
        updated = dict(payload)
        reply = str(updated.get("reply") or "").strip()
        clarification = "借鉴旧版本表现，但仍修改当前新版本；旧版本只作为参考，不会切回去。"
        if clarification not in reply:
            updated["reply"] = f"{clarification}{reply}"
        instruction = str(updated.get("revision_instruction") or "").strip()
        guard = "老师提到旧版本时，只借鉴旧版本表现，但仍修改当前新版本；不要把旧版本 URL 或旧玩法作为执行对象。"
        if guard not in instruction:
            updated["revision_instruction"] = f"{instruction}{guard}"
        return updated

    def _parse_spec(self, current_spec: str) -> dict[str, Any]:
        try:
            payload = json.loads(current_spec)
        except json.JSONDecodeError as exc:
            raise ValueError("当前作品信息不完整，请重新生成一次后再继续修改。") from exc
        if not isinstance(payload, dict):
            raise ValueError("当前作品信息格式不正确，请重新生成一次后再继续修改。")
        return payload

    def _public_history(self, session: ArtifactRevisionSession) -> list[dict[str, str]]:
        return [{"role": item.role, "content": item.content} for item in session.messages[-12:]]


def patch_feedback_from_revision_result(result: dict[str, Any]) -> dict[str, Any]:
    patch_result = (
        result.get("template_revision", {}).get("patch_result")
        if isinstance(result.get("template_revision"), dict)
        else {}
    )
    if isinstance(patch_result, dict) and patch_result.get("teacher_message"):
        return {
            "status": str(patch_result.get("status") or "").strip(),
            "teacher_message": str(patch_result.get("teacher_message") or "").strip(),
            "reason": str(patch_result.get("reason") or "").strip(),
            "recommended_template_id": str(patch_result.get("recommended_template_id") or "").strip(),
            "rejected_paths": (
                patch_result.get("rejected_paths", [])
                if isinstance(patch_result.get("rejected_paths"), list)
                else []
            ),
            "applied_summary": str(patch_result.get("applied_summary") or "").strip(),
        }
    spec = result.get("spec") if isinstance(result.get("spec"), dict) else {}
    return patch_feedback_from_spec(spec)


def patch_feedback_from_spec(spec_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec_payload, dict):
        return {}
    handoff = spec_payload.get("frontend_handoff_contract") if isinstance(spec_payload.get("frontend_handoff_contract"), dict) else {}
    presentation = handoff.get("presentation_inputs") if isinstance(handoff.get("presentation_inputs"), dict) else {}
    patch_feedback = presentation.get("patch_feedback") if isinstance(presentation.get("patch_feedback"), dict) else {}
    teacher_message = str(patch_feedback.get("latest_teacher_message") or "").strip()
    if teacher_message:
        return {
            "status": str(patch_feedback.get("latest_status") or "").strip(),
            "teacher_message": teacher_message,
            "reason": str(patch_feedback.get("latest_reason") or "").strip(),
            "recommended_template_id": str(patch_feedback.get("latest_recommended_template_id") or "").strip(),
            "rejected_paths": (
                patch_feedback.get("latest_rejected_paths", [])
                if isinstance(patch_feedback.get("latest_rejected_paths"), list)
                else []
            ),
        }

    workflow = spec_payload.get("template_workflow") if isinstance(spec_payload.get("template_workflow"), dict) else {}
    variant = workflow.get("game_variant_spec") if isinstance(workflow.get("game_variant_spec"), dict) else {}
    history = variant.get("revision_history") if isinstance(variant.get("revision_history"), list) else []
    latest = next(
        (
            item
            for item in reversed(history)
            if isinstance(item, dict)
            and item.get("revision_type") == "patch_rejected"
            and str(item.get("teacher_message") or "").strip()
        ),
        {},
    )
    if not latest:
        return {}
    return {
        "status": "rejected",
        "teacher_message": str(latest.get("teacher_message") or "").strip(),
        "reason": str(latest.get("reason") or "").strip(),
        "recommended_template_id": str(latest.get("recommended_template_id") or "").strip(),
        "rejected_paths": latest.get("rejected_paths", []) if isinstance(latest.get("rejected_paths"), list) else [],
    }
