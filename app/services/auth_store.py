from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import smtplib
import sqlite3
import string
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.env_bootstrap import ensure_env_loaded
from app.services.runtime_paths import runtime_root


REGISTER_PURPOSE = "register"
RESET_PASSWORD_PURPOSE = "reset_password"
SESSION_COOKIE_NAME = "music_agent_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30
CODE_TTL_MINUTES = 10
CODE_MAX_ATTEMPTS = 5
PASSWORD_MIN_LENGTH = 8
SMTP_CONFIG_ERROR_MESSAGE = "邮箱验证码服务未配置，无法注册或重置密码。请先设置 SMTP_HOST、SMTP_FROM 等环境变量。"


class AuthError(ValueError):
    pass


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    email: str


class AuthStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        configured = db_path or os.environ.get("MUSIC_AGENT_AUTH_DB", "").strip()
        self.db_path = Path(configured).expanduser() if configured else runtime_root() / "auth.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                  id TEXT PRIMARY KEY,
                  email TEXT NOT NULL UNIQUE,
                  email_verified INTEGER NOT NULL DEFAULT 0,
                  password_hash TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS email_codes (
                  id TEXT PRIMARY KEY,
                  email TEXT NOT NULL,
                  purpose TEXT NOT NULL,
                  code_hash TEXT NOT NULL,
                  code_salt TEXT NOT NULL,
                  expires_at TEXT NOT NULL,
                  attempts INTEGER NOT NULL DEFAULT 0,
                  consumed_at TEXT NOT NULL DEFAULT '',
                  created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_email_codes_lookup
                  ON email_codes(email, purpose, created_at);

                CREATE TABLE IF NOT EXISTS sessions (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                  token_hash TEXT NOT NULL UNIQUE,
                  expires_at TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_token_hash
                  ON sessions(token_hash);

                CREATE TABLE IF NOT EXISTS artifacts (
                  id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                  title TEXT NOT NULL,
                  activity_type TEXT NOT NULL,
                  page_url TEXT NOT NULL,
                  file_path TEXT NOT NULL,
                  spec_json TEXT NOT NULL,
                  brain_json TEXT NOT NULL,
                  execution_json TEXT NOT NULL,
                  lesson_analysis_json TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_artifacts_user_updated
                  ON artifacts(user_id, updated_at DESC);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_user_page
                  ON artifacts(user_id, page_url);
                """
            )

    def request_register_code(self, email: str) -> None:
        email = normalize_email(email)
        with self._connect() as conn:
            existing = conn.execute("SELECT email_verified FROM users WHERE email = ?", (email,)).fetchone()
            if existing and int(existing["email_verified"]):
                raise AuthError("这个邮箱已经注册，请直接登录。")
        code = self._create_code(email, REGISTER_PURPOSE)
        self._send_email_code(email, code, "注册验证码")

    def complete_register(self, email: str, code: str, password: str, confirm_password: str) -> tuple[AuthUser, str]:
        email = normalize_email(email)
        validate_passwords(password, confirm_password)
        self._consume_code(email, REGISTER_PURPOSE, code)
        now = utc_now()
        password_hash = hash_password(password)
        with self._connect() as conn:
            existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                user_id = existing["id"]
                conn.execute(
                    """
                    UPDATE users
                    SET email_verified = 1, password_hash = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (password_hash, now, user_id),
                )
            else:
                user_id = uuid4().hex
                conn.execute(
                    """
                    INSERT INTO users (id, email, email_verified, password_hash, created_at, updated_at)
                    VALUES (?, ?, 1, ?, ?, ?)
                    """,
                    (user_id, email, password_hash, now, now),
                )
        token = self.create_session(user_id)
        return AuthUser(user_id=user_id, email=email), token

    def login(self, email: str, password: str) -> tuple[AuthUser, str]:
        email = normalize_email(email)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, email, email_verified, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        if not row or not int(row["email_verified"]) or not verify_password(password, row["password_hash"]):
            raise AuthError("邮箱或密码不正确。")
        token = self.create_session(row["id"])
        return AuthUser(user_id=row["id"], email=row["email"]), token

    def create_dev_session(self, email: str = "developer@local.dev") -> tuple[AuthUser, str]:
        email = normalize_email(email)
        now = utc_now()
        with self._connect() as conn:
            row = conn.execute("SELECT id, email FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                user_id = row["id"]
                conn.execute(
                    "UPDATE users SET email_verified = 1, updated_at = ? WHERE id = ?",
                    (now, user_id),
                )
            else:
                user_id = uuid4().hex
                conn.execute(
                    """
                    INSERT INTO users (id, email, email_verified, password_hash, created_at, updated_at)
                    VALUES (?, ?, 1, ?, ?, ?)
                    """,
                    (user_id, email, hash_password(secrets.token_urlsafe(32)), now, now),
                )
        token = self.create_session(user_id)
        return AuthUser(user_id=user_id, email=email), token

    def request_password_reset_code(self, email: str) -> None:
        email = normalize_email(email)
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ? AND email_verified = 1",
                (email,),
            ).fetchone()
        if not existing:
            raise AuthError("这个邮箱还没有注册。")
        code = self._create_code(email, RESET_PASSWORD_PURPOSE)
        self._send_email_code(email, code, "重置密码验证码")

    def reset_password(self, email: str, code: str, password: str, confirm_password: str) -> tuple[AuthUser, str]:
        email = normalize_email(email)
        validate_passwords(password, confirm_password)
        self._consume_code(email, RESET_PASSWORD_PURPOSE, code)
        now = utc_now()
        password_hash = hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, email FROM users WHERE email = ? AND email_verified = 1",
                (email,),
            ).fetchone()
            if not row:
                raise AuthError("这个邮箱还没有注册。")
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (password_hash, now, row["id"]),
            )
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
        token = self.create_session(row["id"])
        return AuthUser(user_id=row["id"], email=row["email"]), token

    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        now = utc_now()
        expires_at = iso_after(seconds=SESSION_MAX_AGE_SECONDS)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, user_id, token_hash, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uuid4().hex, user_id, hash_token(token), expires_at, now),
            )
        return token

    def user_from_session_token(self, token: str) -> AuthUser | None:
        token = (token or "").strip()
        if not token:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT users.id, users.email, sessions.expires_at
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND users.email_verified = 1
                """,
                (hash_token(token),),
            ).fetchone()
            if not row:
                return None
            if parse_iso(row["expires_at"]) <= datetime.now(timezone.utc):
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
                return None
        return AuthUser(user_id=row["id"], email=row["email"])

    def logout(self, token: str) -> None:
        if not token:
            return
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))

    def save_artifact(self, user_id: str, payload: dict[str, Any], artifact_id: str = "") -> dict[str, Any]:
        now = utc_now()
        public_payload = dict(payload or {})
        spec = public_payload.get("spec") if isinstance(public_payload.get("spec"), dict) else {}
        title = str(spec.get("title") or "音乐课堂工具").strip() or "音乐课堂工具"
        activity_type = str(spec.get("activity_type") or "music_tool").strip() or "music_tool"
        page_url = str(public_payload.get("page_url") or "").strip()
        file_path = str(public_payload.get("file_path") or "").strip()
        if not page_url:
            return public_payload

        brain = public_payload.get("brain") if isinstance(public_payload.get("brain"), dict) else {}
        execution = public_payload.get("execution") if isinstance(public_payload.get("execution"), dict) else {}
        lesson_analysis = (
            public_payload.get("lesson_analysis") if isinstance(public_payload.get("lesson_analysis"), dict) else {}
        )
        existing_id = artifact_id.strip()
        with self._connect() as conn:
            row = None
            if existing_id:
                row = conn.execute(
                    "SELECT id FROM artifacts WHERE id = ? AND user_id = ?",
                    (existing_id, user_id),
                ).fetchone()
            if row is None:
                row = conn.execute(
                    "SELECT id FROM artifacts WHERE user_id = ? AND page_url = ?",
                    (user_id, page_url),
                ).fetchone()
            record_id = row["id"] if row else uuid4().hex[:12]
            public_payload["artifact_id"] = record_id
            payload_json = json.dumps(public_payload, ensure_ascii=False)
            values = (
                record_id,
                user_id,
                title,
                activity_type,
                page_url,
                file_path,
                json.dumps(spec, ensure_ascii=False),
                json.dumps(brain, ensure_ascii=False),
                json.dumps(execution, ensure_ascii=False),
                json.dumps(lesson_analysis, ensure_ascii=False),
                payload_json,
                now,
                now,
            )
            conn.execute(
                """
                INSERT INTO artifacts (
                  id, user_id, title, activity_type, page_url, file_path,
                  spec_json, brain_json, execution_json, lesson_analysis_json,
                  payload_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  title = excluded.title,
                  activity_type = excluded.activity_type,
                  page_url = excluded.page_url,
                  file_path = excluded.file_path,
                  spec_json = excluded.spec_json,
                  brain_json = excluded.brain_json,
                  execution_json = excluded.execution_json,
                  lesson_analysis_json = excluded.lesson_analysis_json,
                  payload_json = excluded.payload_json,
                  updated_at = excluded.updated_at
                """,
                values,
            )
        public_payload["created_at"] = public_payload.get("created_at") or now
        public_payload["updated_at"] = now
        return public_payload

    def list_artifacts(self, user_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, payload_json, created_at, updated_at
                FROM artifacts
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            ).fetchall()
        artifacts: list[dict[str, Any]] = []
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except json.JSONDecodeError:
                payload = {}
            if not isinstance(payload, dict):
                payload = {}
            payload["artifact_id"] = row["id"]
            payload["created_at"] = row["created_at"]
            payload["updated_at"] = row["updated_at"]
            artifacts.append(payload)
        return artifacts

    def get_artifact(self, user_id: str, artifact_id: str) -> dict[str, Any] | None:
        artifact_id = str(artifact_id or "").strip()
        if not artifact_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, payload_json, created_at, updated_at
                FROM artifacts
                WHERE user_id = ? AND id = ?
                """,
                (user_id, artifact_id),
            ).fetchone()
        if not row:
            return None
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        payload["artifact_id"] = row["id"]
        payload["created_at"] = row["created_at"]
        payload["updated_at"] = row["updated_at"]
        return payload

    def delete_artifact(self, user_id: str, artifact_id: str) -> dict[str, Any] | None:
        artifact = self.get_artifact(user_id, artifact_id)
        if artifact is None:
            return None
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM artifacts WHERE user_id = ? AND id = ?",
                (user_id, str(artifact_id or "").strip()),
            )
        return artifact

    def _create_code(self, email: str, purpose: str) -> str:
        code = "".join(secrets.choice(string.digits) for _ in range(6))
        salt = secrets.token_hex(16)
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO email_codes (
                  id, email, purpose, code_hash, code_salt, expires_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid4().hex,
                    email,
                    purpose,
                    hash_code(code, salt),
                    salt,
                    iso_after(minutes=CODE_TTL_MINUTES),
                    now,
                ),
            )
        return code

    def _consume_code(self, email: str, purpose: str, code: str) -> None:
        code = str(code or "").strip()
        if not code:
            raise AuthError("请输入邮箱验证码。")
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, code_hash, code_salt, expires_at, attempts, consumed_at
                FROM email_codes
                WHERE email = ? AND purpose = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (email, purpose),
            ).fetchone()
            if not row or row["consumed_at"]:
                raise AuthError("验证码不正确或已经失效。")
            if parse_iso(row["expires_at"]) <= datetime.now(timezone.utc):
                raise AuthError("验证码已过期，请重新获取。")
            if int(row["attempts"]) >= CODE_MAX_ATTEMPTS:
                raise AuthError("验证码尝试次数过多，请重新获取。")
            if not hmac.compare_digest(hash_code(code, row["code_salt"]), row["code_hash"]):
                conn.execute("UPDATE email_codes SET attempts = attempts + 1 WHERE id = ?", (row["id"],))
                raise AuthError("验证码不正确。")
            conn.execute("UPDATE email_codes SET consumed_at = ? WHERE id = ?", (utc_now(), row["id"]))

    def _send_email_code(self, email: str, code: str, subject: str) -> None:
        smtp_config = smtp_config_status()
        if not smtp_config["configured"]:
            raise AuthError(str(smtp_config["error"]))
        host = str(smtp_config["host"])
        port = int(smtp_config["port"])
        username = str(smtp_config["username"])
        password = os.environ.get("SMTP_PASSWORD", "")
        sender = str(smtp_config["sender"])
        use_tls = bool(smtp_config["use_tls"])
        use_ssl = bool(smtp_config["use_ssl"])

        message = EmailMessage()
        message["Subject"] = f"不亦乐乎音乐智能体 - {subject}"
        message["From"] = sender
        message["To"] = email
        message.set_content(
            f"你的验证码是：{code}\n\n"
            f"验证码 {CODE_TTL_MINUTES} 分钟内有效，请勿转发给他人。\n"
            "如果不是你本人操作，可以忽略这封邮件。"
        )
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(host, port, timeout=15) as smtp:
            if use_tls:
                smtp.starttls()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)


def smtp_config_status() -> dict[str, Any]:
    ensure_env_loaded()
    host = os.environ.get("SMTP_HOST", "").strip()
    raw_port = os.environ.get("SMTP_PORT", "587").strip() or "587"
    username = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    sender = os.environ.get("SMTP_FROM", "").strip() or username
    raw_use_ssl = os.environ.get("SMTP_USE_SSL", "").strip().lower()
    use_ssl = raw_use_ssl in {"1", "true", "yes"} or (not raw_use_ssl and raw_port == "465")
    use_tls = (
        os.environ.get("SMTP_USE_TLS", "true").strip().lower() not in {"0", "false", "no"}
        and not use_ssl
    )
    missing = []
    if not host:
        missing.append("SMTP_HOST")
    if not sender:
        missing.append("SMTP_FROM")
    if username and not password:
        missing.append("SMTP_PASSWORD")

    try:
        port = int(raw_port)
    except ValueError:
        return {
            "configured": False,
            "host": host,
            "port": raw_port,
            "username": username,
            "sender": sender,
            "use_tls": use_tls,
            "use_ssl": use_ssl,
            "missing": missing,
            "error": "邮箱验证码服务配置错误：SMTP_PORT 必须是数字。",
        }
    if port <= 0 or port > 65535:
        return {
            "configured": False,
            "host": host,
            "port": port,
            "username": username,
            "sender": sender,
            "use_tls": use_tls,
            "use_ssl": use_ssl,
            "missing": missing,
            "error": "邮箱验证码服务配置错误：SMTP_PORT 必须在 1 到 65535 之间。",
        }

    error = ""
    if missing:
        error = f"邮箱验证码服务未配置，无法注册或重置密码。请先设置 {', '.join(missing)} 等环境变量。"

    return {
        "configured": not missing,
        "host": host,
        "port": port,
        "username": username,
        "sender": sender,
        "use_tls": use_tls,
        "use_ssl": use_ssl,
        "missing": missing,
        "error": error,
    }


def normalize_email(email: str) -> str:
    normalized = str(email or "").strip().lower()
    if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
        raise AuthError("请输入有效的邮箱地址。")
    return normalized


def validate_passwords(password: str, confirm_password: str) -> None:
    if password != confirm_password:
        raise AuthError("两次输入的密码不一致。")
    if len(password or "") < PASSWORD_MIN_LENGTH:
        raise AuthError(f"密码至少需要 {PASSWORD_MIN_LENGTH} 位。")


def hash_password(password: str) -> str:
    iterations = 260_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
        return hmac.compare_digest(candidate, digest)
    except Exception:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_code(code: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{code}".encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_after(*, minutes: int = 0, seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes, seconds=seconds)).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)
