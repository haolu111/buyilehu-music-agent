from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Message:
    role: str  # system, user, assistant, tool, observation
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSession:
    session_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    messages: list[Message] = field(default_factory=list)
    state: str = "idle"  # idle, understanding, planning, generating, reviewing, fixing, delivering
    current_artifact: dict[str, Any] = field(default_factory=dict)
    iterations: int = 0
    max_iterations: int = 10
    context: dict[str, Any] = field(default_factory=dict)
    busy: bool = False

    def add_message(self, role: str, content: str, **metadata) -> None:
        self.messages.append(Message(role=role, content=content, metadata=metadata))
        self.updated_at = time.time()

    def get_recent_messages(self, n: int = 20) -> list[Message]:
        return self.messages[-n:]

    def to_llm_messages(self, system_prompt: str | None = None) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for msg in self.messages:
            if msg.role in ("user", "assistant", "system"):
                messages.append({"role": msg.role, "content": msg.content})
            elif msg.role == "observation":
                messages.append({"role": "user", "content": f"[执行结果] {msg.content}"})
            elif msg.role == "tool":
                messages.append({"role": "user", "content": f"[工具返回] {msg.content}"})
        return messages

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)

    def set_context(self, key: str, value: Any) -> None:
        self.context[key] = value


class ConversationMemory:
    def __init__(self):
        self._sessions: dict[str, AgentSession] = {}
        self._lock = threading.RLock()

    def create_session(self) -> AgentSession:
        with self._lock:
            session_id = uuid4().hex[:12]
            session = AgentSession(session_id=session_id)
            self._sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> AgentSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "session_id": s.session_id,
                    "state": s.state,
                    "iterations": s.iterations,
                    "message_count": len(s.messages),
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "busy": s.busy,
                }
                for s in self._sessions.values()
            ]

    def cleanup_old_sessions(self, max_age_seconds: float = 3600) -> int:
        with self._lock:
            now = time.time()
            to_delete = [
                sid for sid, s in self._sessions.items()
                if now - s.updated_at > max_age_seconds and not s.busy
            ]
            for sid in to_delete:
                del self._sessions[sid]
            return len(to_delete)

    def begin_session_run(self, session_id: str) -> AgentSession | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if session.busy:
                raise RuntimeError("SESSION_BUSY")
            session.busy = True
            session.updated_at = time.time()
            return session

    def end_session_run(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return
            session.busy = False
            session.updated_at = time.time()


# 全局单例
_memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    return _memory
