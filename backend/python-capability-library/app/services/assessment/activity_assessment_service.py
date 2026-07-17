from __future__ import annotations

import json
import os
from typing import Any

from app.services.core.env_bootstrap import ensure_env_loaded
from app.services.orchestration.package_design_agent import (
    _call_model_messages,
    _doubao_config,
    _ecnu_config,
    _short_error,
)
from app.services.instruments.instrument_task_service import evaluate_instrument_task


def assess_activity_submission(
    *,
    activity_id: str,
    renderer: str,
    title: str,
    result: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    ensure_env_loaded()
    mode = str(assessment.get("mode") or "completion")
    if mode == "rule":
        score, feedback = _rule_score(renderer=renderer, result=result, assessment=assessment)
        return _result(score=score, mode="rule", provider="system", feedback=feedback)
    if mode == "instrument_evidence":
        task = assessment.get("task") if isinstance(assessment.get("task"), dict) else {}
        events = result.get("events") if isinstance(result.get("events"), list) else []
        evidence = evaluate_instrument_task(task, events)
        score = evidence.get("objective_score")
        payload = _result(
            score=int(score) if isinstance(score, (int, float)) else None,
            mode="instrument_evidence",
            provider="system",
            feedback="已按节拍、音高和事件顺序生成客观证据；表现力与合作质量由教师确认。",
        )
        payload["evidence"] = evidence
        return payload
    if mode == "ai":
        return _ai_score(
            activity_id=activity_id,
            renderer=renderer,
            title=title,
            result=result,
            assessment=assessment,
        )
    score = assessment.get("scoreOnComplete")
    return _result(
        score=int(score) if isinstance(score, (int, float)) else None,
        mode="completion",
        provider="system",
        feedback="活动已完成，本环节不进行能力评分。" if score is None else "已按完成要求记录。",
    )


def _rule_score(*, renderer: str, result: dict[str, Any], assessment: dict[str, Any]) -> tuple[int, str]:
    answer_key = assessment.get("answerKey") if isinstance(assessment.get("answerKey"), dict) else {}
    if renderer in {"rhythm-drag", "solfege-sort"}:
        return _sequence_score(result.get("sequence"), answer_key.get("sequence"))
    if renderer == "melody-trace":
        return _sequence_score(result.get("trace"), answer_key.get("trace"))
    if renderer == "form-order":
        return _sequence_score(result.get("order"), answer_key.get("order"))
    if renderer == "timbre-match":
        expected = answer_key.get("matches") if isinstance(answer_key.get("matches"), dict) else {}
        actual = result.get("matches") if isinstance(result.get("matches"), dict) else {}
        if not expected:
            return 70, "已完成音色配对，当前题目没有标准答案配置。"
        correct = sum(1 for key, value in expected.items() if str(actual.get(key)) == str(value))
        score = round(100 * correct / len(expected))
        return score, f"配对正确 {correct}/{len(expected)} 项。"
    if renderer == "listening-choice":
        score = (35 if result.get("choice") else 0) + (35 if result.get("evidence") else 0)
        explanation = str(result.get("explanation") or "").strip()
        score += 30 if len(explanation) >= 8 else 15 if explanation else 0
        return score, "已根据选择、音乐依据和理由完整度评分。"
    if renderer == "singing-practice":
        attempts = _number(result.get("attempts"))
        duration = _number(result.get("durationSeconds"))
        score = min(100, 45 + min(attempts, 3) * 10 + min(duration, 25))
        return score, "已根据练唱次数和有效录音时长评分；音准评价仍需教师听评。"
    return 70, "已根据任务完成情况评分。"


def _sequence_score(actual_value: Any, expected_value: Any) -> tuple[int, str]:
    actual = actual_value if isinstance(actual_value, list) else []
    expected = expected_value if isinstance(expected_value, list) else []
    if not expected:
        return 70 if actual else 0, "当前题目没有答案键，按完成度记录。"
    correct = sum(1 for index, value in enumerate(expected) if index < len(actual) and str(actual[index]) == str(value))
    score = round(100 * correct / len(expected))
    return score, f"顺序正确 {correct}/{len(expected)} 项。"


def _ai_score(
    *, activity_id: str,
    renderer: str,
    title: str,
    result: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    messages = _assessment_messages(
        activity_id=activity_id,
        renderer=renderer,
        title=title,
        result=result,
        rubric=assessment.get("rubric"),
    )
    ecnu_config = _ecnu_config()
    score_model = os.getenv("CHAT_ECNU_SCORE_MODEL") or ""
    if score_model:
        ecnu_config["model"] = score_model
        ecnu_config["enabled"] = bool(ecnu_config.get("api_key") and score_model)
    for config in (ecnu_config, _doubao_config()):
        if not config.get("enabled"):
            errors.append(f"{config['provider']}: not configured")
            continue
        try:
            payload = _call_model_messages(config, messages=messages, max_tokens=700)
            score = max(0, min(100, int(payload.get("score"))))
            feedback = str(payload.get("feedback") or "已完成作品评价。").strip()[:300]
            dimensions = payload.get("dimensions") if isinstance(payload.get("dimensions"), dict) else {}
            result_payload = _result(score=score, mode="ai", provider=config["provider"], feedback=feedback)
            result_payload["model"] = config.get("model")
            result_payload["dimensions"] = dimensions
            result_payload["fallbackReason"] = "; ".join(errors) or None
            return result_payload
        except Exception as exc:
            errors.append(f"{config['provider']}: {_short_error(exc)}")

    score = _creative_fallback_score(renderer=renderer, result=result)
    payload = _result(score=score, mode="ai_fallback", provider="system", feedback="模型暂不可用，已按作品完成度临时评分。")
    payload["fallbackReason"] = "; ".join(errors)
    return payload


def _assessment_messages(
    *, activity_id: str, renderer: str, title: str, result: dict[str, Any], rubric: Any,
) -> list[dict[str, str]]:
    system = (
        "你是小学音乐课堂评价 Agent。只输出 JSON，不评价学生人格，不虚构未提交的声音或作品证据。"
        "按 rubric 对提交结果评分，返回 0-100 整数。反馈使用一到两句适合小学生的具体中文。"
    )
    user = json.dumps({
        "activity_id": activity_id,
        "renderer": renderer,
        "title": title,
        "submission": result,
        "rubric": rubric,
        "output_schema": {
            "score": 0,
            "feedback": "具体反馈",
            "dimensions": {"任务完成度": 0, "音乐要素运用": 0, "表达与创意": 0},
        },
    }, ensure_ascii=False, separators=(",", ":"))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _creative_fallback_score(*, renderer: str, result: dict[str, Any]) -> int:
    if renderer == "creation-panel":
        return min(90, 55 + min(len(str(result.get("notes") or "")), 70) // 2)
    if renderer == "virtual-instrument":
        notes = result.get("notes") if isinstance(result.get("notes"), list) else []
        return min(90, 50 + min(len(notes), 10) * 3 + min(len(set(map(str, notes))), 5) * 2)
    if renderer == "ensemble-roles":
        steps = result.get("completedSteps") if isinstance(result.get("completedSteps"), list) else []
        return min(90, 55 + len(steps) * 8 + (10 if result.get("role") else 0))
    return 70


def _number(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _result(*, score: int | None, mode: str, provider: str, feedback: str) -> dict[str, Any]:
    return {"score": score, "mode": mode, "provider": provider, "feedback": feedback}
