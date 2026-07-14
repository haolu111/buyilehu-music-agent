from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Optional
from uuid import uuid4

from app.services.agent_brain import complete_brain_report, prepare_brain_report
from app.services.execution_orchestrator import finalize_execution, initialize_execution
from app.services.generation_contracts import attach_visual_asset_pack, lock_spec_to_activity_type
from app.services.image_generation_skill import attach_generated_visual_assets
from app.services.lightweight_revision import try_lightweight_revision
from app.services.music_logic_contract import validate_music_logic_contract
from app.services.opencode_runtime import (
    materialize_opencode_package,
    opencode_status,
    run_opencode_task,
    write_agent_brain_report,
)
from app.services.performance_template_library import apply_performance_template_if_applicable
from app.services.playable_scaffold_registry import classify_playable_scaffold
from app.services.runtime_paths import output_url_for_path
from app.services.webpage_generator import (
    ensure_listening_tool_contract,
    ensure_music_game_playable_contract,
    render_generated_tool,
)


EmitFn = Callable[[str, str, str], None]
SkillsProvider = Callable[[], list[dict[str, Any]]]
LessonContextApplier = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]
ArtifactResolver = Callable[[str, str], Optional[Path]]


class GenerationPipeline:
    """Owns the ordered generation/revision workflow between API and tools."""

    def __init__(
        self,
        *,
        model_gateway: Any,
        output_dir: Path,
        skills_provider: SkillsProvider,
        lesson_context_applier: LessonContextApplier | None = None,
        artifact_resolver: ArtifactResolver | None = None,
    ) -> None:
        self.model_gateway = model_gateway
        self.output_dir = output_dir
        self.skills_provider = skills_provider
        self.lesson_context_applier = lesson_context_applier
        self.artifact_resolver = artifact_resolver

    def generate(
        self,
        need: str,
        *,
        force_local: bool = False,
        emit: EmitFn | None = None,
        generation_mode: str = "fast",
        lesson_context: dict[str, Any] | None = None,
        forced_activity_type: str | None = None,
        prebuilt_spec: dict[str, Any] | None = None,
        model_info_override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        spec, model_info = self._build_initial_spec(
            need,
            force_local=force_local,
            emit=emit,
            generation_mode=generation_mode,
            forced_activity_type=forced_activity_type,
            prebuilt_spec=prebuilt_spec,
            model_info_override=model_info_override,
        )

        if forced_activity_type:
            spec = self._lock_activity(spec, forced_activity_type)
            self._emit(emit, f"已按生成目标锁定产物类型：{forced_activity_type}。", "model-gateway")
        if lesson_context and self.lesson_context_applier:
            spec = self.lesson_context_applier(spec, lesson_context)
            self._emit(emit, "已把课例中间层写入生成规格，后续页面将按教案约束生成。", "lesson-game-designer")
        if forced_activity_type:
            spec = self._lock_activity(spec, forced_activity_type)

        self._emit_blueprint(spec, emit)
        spec, image_generation_report, brain_report = self._prepare_spec_for_artifact(
            need,
            spec,
            emit=emit,
            generation_mode=generation_mode,
            forced_activity_type=forced_activity_type,
            action="generate",
        )

        self._preflight_generation_readiness(spec)
        scaffold_route = self._select_fast_playable_scaffold(
            spec,
            generation_mode=generation_mode,
            lesson_context=lesson_context,
            forced_activity_type=forced_activity_type,
            emit=emit,
        )
        if scaffold_route.get("enabled") and isinstance(scaffold_route.get("spec"), dict):
            spec = scaffold_route["spec"]

        opencode_runtime = opencode_status()
        direct_template_reference = self._should_seed_direct_template(spec, lesson_context=lesson_context, forced_activity_type=forced_activity_type)
        if direct_template_reference:
            spec = self._mark_direct_template_seed(spec)
        if scaffold_route.get("enabled") and not opencode_runtime.get("enabled"):
            raise RuntimeError("OpenCode 未可用，已阻止教案生成退回本地骨架。请检查 OPENCODE_COMMAND。")
        if scaffold_route.get("enabled"):
            index_path, page_url = self._prepare_opencode_first_artifact()
            self._emit(
                emit,
                f"已识别可复用玩法骨架：{scaffold_route.get('label', '可玩骨架')}，仅作为 OpenCode 生成参考，不再跳过 OpenCode。",
                "playable-scaffold",
            )
        elif force_local:
            index_path, page_url = render_generated_tool(spec, self.output_dir)
            self._emit(emit, "已按本地模式生成页面主体。", "frontend-artifact-builder")
        elif opencode_runtime.get("enabled"):
            index_path, page_url = self._prepare_opencode_first_artifact()
            if direct_template_reference:
                self._emit(emit, "直接生成已命中活动母版，但不会写入模板页；OpenCode 只参考配置里的母版说明，必须生成一个新页面。", "opencode-runtime")
            else:
                self._emit(emit, "未命中可用母版，OpenCode 将自由生成页面。", "opencode-runtime")
        else:
            raise RuntimeError("OpenCode 未可用，已阻止退回本地模板。请检查 OPENCODE_COMMAND。")

        execution_report, opencode_package, opencode_run, brain_report = self._run_artifact_execution_loop(
            spec,
            index_path,
            brain_report,
            force_local=force_local,
            opencode_runtime=opencode_runtime,
            generation_mode=generation_mode,
            emit=emit,
            skip_opencode_reason="",
        )
        opencode_package["execution_url"] = execution_report.get("report_url", "")
        self._raise_if_execution_failed(execution_report, emit=emit)

        return {
            "page_url": page_url,
            "file_path": str(index_path),
            "model": model_info,
            "spec": spec,
            "image_generation": image_generation_report,
            "brain": brain_report,
            "execution": execution_report,
            "opencode": opencode_package,
            "opencode_run": opencode_run,
        }

    def revise(
        self,
        *,
        current_spec: str,
        revision: str,
        current_file_path: str = "",
        current_page_url: str = "",
        force_local: bool = False,
        emit: EmitFn | None = None,
        generation_mode: str = "strict",
    ) -> dict[str, Any]:
        if self.artifact_resolver is None:
            raise ValueError("没有配置产物路径解析器，无法修改当前工具。")
        try:
            spec_payload = json.loads(current_spec)
        except json.JSONDecodeError:
            raise ValueError("没有读到当前工具信息，请重新生成一次。")

        requested_mode = self._normalize_generation_mode(generation_mode)
        index_path = self.artifact_resolver(current_file_path, current_page_url)
        if index_path is None:
            raise ValueError("没有找到当前工具文件，请重新生成后再修改。")

        lightweight_result = try_lightweight_revision(
            spec_payload=spec_payload,
            revision=revision,
            index_path=index_path,
            generation_mode=requested_mode,
            emit=emit,
        )
        if lightweight_result is not None:
            return lightweight_result

        self._emit(emit, "开始理解增量修改要求。", "model-gateway")
        need = self.model_gateway.build_revision_need(spec_payload, revision)
        spec, model_info = self.model_gateway.generate_tool_spec(
            need=need,
            skills=self.skills_provider(),
            force_local=force_local,
        )
        # 增量修改默认优先保证“能用”，只在用户明确要求时走严格验收。
        spec["generation_mode"] = "strict" if requested_mode == "strict" else "fast"
        self._emit(emit, "修改规格已生成，进入大脑自检。", "agent-brain")
        spec, brain_report = prepare_brain_report(need, spec, action="revise", revision=revision)

        target_dir = index_path.parent
        self._emit(emit, "已找到当前工具目录，准备执行增量修改。", "execution-orchestrator")
        execution_report = initialize_execution(spec, target_dir, action="revise", revision=revision)
        opencode_package = materialize_opencode_package(spec, target_dir, brain_report=brain_report)
        opencode_run = run_opencode_task(spec, target_dir, action="revise", revision=revision, brain_report=brain_report)
        self._emit(emit, f"OpenCode 增量修改结束：{opencode_run.get('status', 'unknown')}。", "opencode-runtime")

        self._restore_local_contracts_if_allowed(spec, index_path, opencode_run, emit=emit, revision=True)
        brain_report = complete_brain_report(brain_report, spec, opencode_run=opencode_run, artifact_path=index_path)
        opencode_package["brain_url"] = write_agent_brain_report(target_dir, brain_report)

        self._emit(emit, "开始修改后的多智能体验收和修复。", "execution-orchestrator")
        execution_report = finalize_execution(
            spec,
            target_dir,
            action="revise",
            opencode_run=opencode_run,
            brain_report=brain_report,
            existing_report=execution_report,
        )
        opencode_package["execution_url"] = execution_report.get("report_url", "")
        self._raise_if_execution_failed(execution_report, emit=emit)
        self._emit(emit, f"增量修改执行层完成：{execution_report.get('status', 'unknown')}。", "execution-orchestrator")

        return {
            "page_url": output_url_for_path(index_path),
            "file_path": str(index_path),
            "model": model_info,
            "spec": spec,
            "brain": brain_report,
            "execution": execution_report,
            "opencode": opencode_package,
            "opencode_run": opencode_run,
            "revision": revision,
            "incremental": True,
        }

    def _build_initial_spec(
        self,
        need: str,
        *,
        force_local: bool,
        emit: EmitFn | None,
        generation_mode: str,
        forced_activity_type: str | None,
        prebuilt_spec: dict[str, Any] | None,
        model_info_override: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if prebuilt_spec is None:
            self._emit(emit, "开始生成课堂工具规格。", "model-gateway")
            spec, model_info = self.model_gateway.generate_tool_spec(
                need=need,
                skills=self.skills_provider(),
                force_local=force_local,
                forced_activity_type=forced_activity_type,
            )
            spec["generation_mode"] = self._normalize_generation_mode(generation_mode)
            return spec, model_info

        self._emit(emit, "已使用确认后的教案方案生成结构化规格。", "lesson-game-designer")
        model_info = model_info_override or {
            "provider": "lesson_contract",
            "model": "confirmed-lesson-analysis",
        }
        prebuilt_spec = dict(prebuilt_spec)
        prebuilt_spec["generation_mode"] = self._normalize_generation_mode(generation_mode)
        return prebuilt_spec, model_info

    def _prepare_spec_for_artifact(
        self,
        need: str,
        spec: dict[str, Any],
        *,
        emit: EmitFn | None,
        generation_mode: str,
        forced_activity_type: str | None,
        action: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        spec["generation_mode"] = self._normalize_generation_mode(generation_mode)
        spec = apply_performance_template_if_applicable(spec)
        if spec.get("performance", {}).get("template_variant"):
            self._emit(emit, f"已匹配表现模板：{spec['performance'].get('template_label', '表现闯关模板')}。", "performance-template")

        spec = attach_visual_asset_pack(spec)
        self._emit(emit, "正在准备课堂视觉素材：优先生成真实图片，不可用则使用本地素材包。", "image-generation")
        spec, image_generation_report = attach_generated_visual_assets(spec)
        self._emit(emit, f"视觉素材准备完成：{image_generation_report.get('status', 'unknown')}。", "image-generation")

        self._emit(emit, "规格生成完成，进入大脑自检和自动加固。", "agent-brain")
        spec, brain_report = prepare_brain_report(need, spec, action=action)
        if forced_activity_type:
            spec = self._lock_activity(spec, forced_activity_type)
            self._emit(emit, f"最终规格已再次确认生成目标：{forced_activity_type}。", "model-gateway")
        self._emit(emit, f"大脑自检完成：{brain_report['self_critique']['score']} 分。", "agent-brain")
        return spec, image_generation_report, brain_report

    def _run_artifact_execution_loop(
        self,
        spec: dict[str, Any],
        index_path: Path,
        brain_report: dict[str, Any],
        *,
        force_local: bool,
        opencode_runtime: dict[str, Any],
        generation_mode: str,
        emit: EmitFn | None,
        skip_opencode_reason: str = "",
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        spec["generation_mode"] = self._normalize_generation_mode(generation_mode)
        execution_report = initialize_execution(spec, index_path.parent, action="generate")
        opencode_package = materialize_opencode_package(spec, index_path.parent, brain_report=brain_report)
        self._emit(emit, "页面生成信息已整理完成。", "opencode-runtime")
        if skip_opencode_reason:
            opencode_run = self._write_skipped_opencode_run(
                index_path,
                reason=skip_opencode_reason,
                action="generate",
            )
            completed_brain_report = complete_brain_report(brain_report, spec, opencode_run=opencode_run, artifact_path=index_path)
            opencode_package["brain_url"] = write_agent_brain_report(index_path.parent, completed_brain_report)
            self._emit(emit, "开始轻量检查可复用玩法骨架的页面可用性。", "execution-orchestrator")
            execution_report = finalize_execution(
                spec,
                index_path.parent,
                action="generate",
                opencode_run=opencode_run,
                brain_report=completed_brain_report,
                existing_report=execution_report,
            )
            self._emit(emit, "玩法骨架可用性检查完成。", "execution-orchestrator")
            return execution_report, opencode_package, opencode_run, completed_brain_report

        max_attempts = self._opencode_generate_max_attempts(
            force_local=force_local,
            opencode_runtime=opencode_runtime,
            generation_mode=generation_mode,
        )
        lesson_repair_only = self._lesson_game_contract_repair_only(spec)
        strict_mode = self._normalize_generation_mode(generation_mode) == "strict"
        if lesson_repair_only and opencode_runtime.get("enabled") and strict_mode:
            # Contract-guided lesson generation should not spend minutes repairing
            # pages when the remaining failure belongs to the upstream spec.
            max_attempts = min(max(max_attempts, 2), 2)
        opencode_run: dict[str, Any] = {}
        for attempt in range(1, max_attempts + 1):
            repair_current_artifact = lesson_repair_only and attempt > 1 and index_path.exists()
            if attempt > 1 and not repair_current_artifact:
                self._reset_opencode_generated_artifact(index_path)
                self._emit(
                    emit,
                    f"第 {attempt} 次调用 OpenCode 重新生成页面；不使用本地页面修补。",
                    "opencode-runtime",
                    "warning",
                )
            elif repair_current_artifact:
                self._emit(
                    emit,
                    f"第 {attempt} 次调用 OpenCode 修复当前页面；不回退模板，不删除当前产物。",
                    "opencode-runtime",
                    "warning",
                )
            opencode_action = "revise" if repair_current_artifact else "generate"
            opencode_revision = self._opencode_repair_revision(execution_report) if repair_current_artifact else ""
            opencode_run = run_opencode_task(
                spec,
                index_path.parent,
                action=opencode_action,
                revision=opencode_revision,
                brain_report=brain_report,
            )
            self._emit(emit, f"OpenCode 页面生成步骤已完成：{opencode_run.get('status', 'unknown')}。", "opencode-runtime")
            self._restore_local_contracts_if_allowed(spec, index_path, opencode_run, emit=emit)
            self._restore_direct_listening_contract_if_needed(spec, index_path, opencode_run, emit=emit)

            completed_brain_report = complete_brain_report(brain_report, spec, opencode_run=opencode_run, artifact_path=index_path)
            opencode_package["brain_url"] = write_agent_brain_report(index_path.parent, completed_brain_report)
            self._emit(emit, "开始检查页面、音乐逻辑和课堂可用性。", "execution-orchestrator")
            execution_report = finalize_execution(
                spec,
                index_path.parent,
                action="generate",
                opencode_run=opencode_run,
                brain_report=completed_brain_report,
                existing_report=execution_report,
            )
            self._emit(emit, "质量检查完成。", "execution-orchestrator")
            brain_report = completed_brain_report
            if execution_report.get("status") != "failed" or attempt >= max_attempts:
                break
            if lesson_repair_only and index_path.exists():
                if not self._can_retry_current_artifact(execution_report):
                    self._emit(
                        emit,
                        "验收发现的已不是页面层问题，停止继续修补当前页面，避免无效返工。",
                        "execution-orchestrator",
                        "warning",
                    )
                    break
                self._emit(
                    emit,
                    f"OpenCode 第 {attempt} 次产物未通过验收，将继续修复当前页面。",
                    "execution-orchestrator",
                    "warning",
                )
                continue
            self._emit(
                emit,
                f"OpenCode 第 {attempt} 次产物未通过验收，将再次调用 OpenCode 重写。",
                "execution-orchestrator",
                "warning",
            )
        return execution_report, opencode_package, opencode_run, brain_report

    def _restore_local_contracts_if_allowed(
        self,
        spec: dict[str, Any],
        index_path: Path,
        opencode_run: dict[str, Any],
        *,
        emit: EmitFn | None,
        revision: bool = False,
    ) -> None:
        if self._allow_local_contract_restore(opencode_run) and ensure_music_game_playable_contract(spec, index_path):
            message = "已自动恢复音乐小游戏的可操作任务板，避免页面退化成文字规则页。" if revision else "已补齐音乐小游戏的可操作任务板。"
            self._emit(emit, message, "frontend-artifact-builder")
        elif not self._allow_local_contract_restore(opencode_run):
            message = "OpenCode 已启用：跳过本地页面覆盖，执行层将直接验收 OpenCode 增量修改。" if revision else "正在检查 OpenCode 生成后的页面。"
            self._emit(emit, message, "frontend-artifact-builder")

        if self._allow_local_contract_restore(opencode_run) and ensure_listening_tool_contract(spec, index_path):
            self._emit(emit, "已自动恢复聆听编辑页的音乐要素控件和快速变换接口。", "frontend-artifact-builder")

    def _restore_direct_listening_contract_if_needed(
        self,
        spec: dict[str, Any],
        index_path: Path,
        opencode_run: dict[str, Any],
        *,
        emit: EmitFn | None,
    ) -> None:
        if spec.get("activity_type") != "listening" and spec.get("template_id") not in {"Blueprint_Listen", "Template_Listen"}:
            return
        if ensure_listening_tool_contract(spec, index_path):
            self._mark_contract_restored_run(index_path, opencode_run, reason="listening_contract_restored")
            self._emit(
                emit,
                "已恢复聆听工具硬契约：上传音频、MIDI 要素变换、对比试听和真实采样播放链路不能被 OpenCode 改丢。",
                "frontend-artifact-builder",
                "warning",
            )

    def _emit_blueprint(self, spec: dict[str, Any], emit: EmitFn | None) -> None:
        blueprint_plan = spec.get("blueprint_plan", {}) if isinstance(spec.get("blueprint_plan"), dict) else {}
        if not blueprint_plan and str(spec.get("artifact_generation_mode") or "") != "freeform":
            return
        if spec.get("activity_type") == "music_game" and str(spec.get("artifact_generation_mode") or "") == "freeform":
            self._emit(
                emit,
                "当前玩法未命中现成模板，将按教案、歌曲材料和音乐逻辑契约自由生成主游戏页面。",
                "model-gateway",
            )
            return
        self._emit(
            emit,
            f"已选定活动母版：{blueprint_plan.get('blueprint_label', spec.get('template_id', '未指定'))}；主玩法：{blueprint_plan.get('primary_interaction', '未指定')}。",
            "model-gateway",
        )

    def _lock_activity(self, spec: dict[str, Any], activity_type: str) -> dict[str, Any]:
        return lock_spec_to_activity_type(spec, activity_type, self.model_gateway)

    def _prepare_opencode_first_artifact(self) -> tuple[Path, str]:
        tool_id = uuid4().hex[:10]
        target_dir = self.output_dir / "generated_tools" / tool_id
        target_dir.mkdir(parents=True, exist_ok=True)
        index_path = target_dir / "index.html"
        return index_path, output_url_for_path(index_path)

    def _select_fast_playable_scaffold(
        self,
        spec: dict[str, Any],
        *,
        generation_mode: str,
        lesson_context: dict[str, Any] | None,
        forced_activity_type: str | None,
        emit: EmitFn | None,
    ) -> dict[str, Any]:
        if not lesson_context and not forced_activity_type:
            return {
                "enabled": False,
                "reason": "直接生成链路不使用可复用骨架：有模板则模板种子增量生成，无模板则 OpenCode 自由生成。",
            }
        route = classify_playable_scaffold(spec, generation_mode=self._normalize_generation_mode(generation_mode))
        if route.get("enabled"):
            self._emit(
                emit,
                f"快速模式识别到{route.get('label', '可玩骨架')}：将作为 OpenCode 参考结构，不作为本地生成结果。",
                "playable-scaffold",
            )
        return route

    @staticmethod
    def _write_skipped_opencode_run(index_path: Path, *, reason: str, action: str) -> dict[str, Any]:
        run_path = index_path.parent / "config" / "opencode-run.json"
        run_path.parent.mkdir(parents=True, exist_ok=True)
        result = {
            "enabled": False,
            "executed": False,
            "status": "skipped",
            "reason": reason or "命中快速可玩骨架，已跳过 OpenCode。",
            "action": action,
            "index_changed": True,
            "artifact_changed": True,
            "changed_files": ["index.html"],
            "restored_fallback": False,
            "missing_required_artifact": False,
        }
        run_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        result["run_url"] = output_url_for_path(run_path)
        return result

    @staticmethod
    def _mark_contract_restored_run(index_path: Path, opencode_run: dict[str, Any], *, reason: str) -> None:
        opencode_run["contract_restored"] = True
        opencode_run["contract_restore_reason"] = reason
        opencode_run["missing_required_artifact"] = False
        opencode_run["index_changed"] = True
        opencode_run["artifact_changed"] = True
        changed_files = opencode_run.setdefault("changed_files", [])
        if isinstance(changed_files, list) and "index.html" not in changed_files:
            changed_files.append("index.html")
        validation_errors = opencode_run.get("validation_errors")
        if isinstance(validation_errors, list):
            opencode_run["validation_errors"] = [
                item for item in validation_errors if str(item).strip() != "index.html missing"
            ]
        run_path = index_path.parent / "config" / "opencode-run.json"
        if run_path.exists():
            run_path.write_text(json.dumps(opencode_run, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _should_seed_direct_template(
        spec: dict[str, Any],
        *,
        lesson_context: dict[str, Any] | None,
        forced_activity_type: str | None,
    ) -> bool:
        if lesson_context or forced_activity_type:
            return False
        if spec.get("lesson_context") or spec.get("lesson_game_contract"):
            return False
        return str(spec.get("artifact_generation_mode") or "") == "template" and bool(str(spec.get("template_id") or "").strip())

    @staticmethod
    def _mark_direct_template_seed(spec: dict[str, Any]) -> dict[str, Any]:
        generation_strategy = dict(spec.get("generation_strategy", {})) if isinstance(spec.get("generation_strategy"), dict) else {}
        generation_strategy["direct_generation_route"] = "template_reference_then_opencode_generate"
        generation_strategy["template_seed_required"] = False
        generation_strategy["template_reference_only"] = True
        generation_strategy.setdefault(
            "opencode_execution_target",
            "参考活动母版的结构能力与交互要点，但由 OpenCode 主导生成当前网页；模板只能参考，不能整页照抄或直接作为结果。",
        )
        return {
            **spec,
            "direct_generation_route": "template_reference_then_opencode_generate",
            "generation_strategy": generation_strategy,
        }

    @staticmethod
    def _allow_local_contract_restore(opencode_run: dict[str, Any]) -> bool:
        return not bool(opencode_run.get("enabled"))

    @staticmethod
    def _opencode_generate_max_attempts(*, force_local: bool, opencode_runtime: dict[str, Any], generation_mode: str) -> int:
        if force_local or not opencode_runtime.get("enabled"):
            return 1
        if str(generation_mode or "").strip().lower() == "fast":
            return 1
        raw = os.getenv("OPENCODE_GENERATE_MAX_ATTEMPTS", "2").strip()
        try:
            return max(1, min(4, int(raw)))
        except ValueError:
            return 2

    @staticmethod
    def _normalize_generation_mode(value: str) -> str:
        mode = str(value or "").strip().lower()
        return mode if mode in {"fast", "strict"} else "fast"

    @staticmethod
    def _lesson_game_contract_repair_only(spec: dict[str, Any]) -> bool:
        policy = spec.get("lesson_generation_policy", {}) if isinstance(spec.get("lesson_generation_policy"), dict) else {}
        return (
            spec.get("activity_type") == "music_game"
            and bool(spec.get("lesson_game_contract"))
            and str(policy.get("repair_strategy") or "") == "opencode_repair_current_artifact_only"
        )

    @staticmethod
    def _opencode_repair_revision(execution_report: dict[str, Any]) -> str:
        lines = [
            "请修复当前 index.html，使其通过执行层验收；不要重做成模板页，不要回退本地模板。",
            "必须保留教案游戏契约、音乐逻辑契约、真实音色要求和当前已生成的有效交互。",
        ]
        summary = str(execution_report.get("summary") or "").strip()
        if summary:
            lines.append(f"验收摘要：{summary}")
        results = execution_report.get("results", {})
        if isinstance(results, dict):
            for result in results.values():
                if not isinstance(result, dict):
                    continue
                for check in result.get("checks", []) if isinstance(result.get("checks"), list) else []:
                    if isinstance(check, dict) and check.get("status") == "fail":
                        lines.append(f"- 修复失败项：{check.get('label', check.get('id', 'unknown'))}；原因：{check.get('message', '')}")
        return "\n".join(lines[:18])

    @staticmethod
    def _reset_opencode_generated_artifact(index_path: Path) -> None:
        target_dir = index_path.parent
        for filename in ["index.html", "styles.css", "app.js"]:
            path = target_dir / filename
            if path.exists() and path.is_file():
                path.unlink()

    @staticmethod
    def _emit(emit: EmitFn | None, message: str, agent: str = "system", level: str = "info") -> None:
        if emit:
            emit(message, agent, level)

    def _raise_if_execution_failed(self, execution_report: dict[str, Any], *, emit: EmitFn | None = None) -> None:
        if execution_report.get("status") != "failed":
            return

        summary = str(execution_report.get("summary") or "执行层验收未通过。").strip()
        results = execution_report.get("results", {})
        frontend_result = results.get("frontend_artifact_builder", {}) if isinstance(results, dict) else {}
        frontend_details = frontend_result.get("details", {}) if isinstance(frontend_result, dict) else {}
        missing_required_artifact = bool(frontend_details.get("missing_required_artifact"))
        restored_fallback = bool(frontend_details.get("restored_fallback"))
        artifact_bytes = int(frontend_details.get("bytes") or 0)

        if missing_required_artifact or restored_fallback or artifact_bytes <= 0:
            failed_reasons: list[str] = []
            if isinstance(results, dict):
                for agent_id, result in results.items():
                    if not isinstance(result, dict) or result.get("status") != "failed":
                        continue
                    checks = result.get("checks", [])
                    if not isinstance(checks, list):
                        continue
                    for check in checks:
                        if not isinstance(check, dict) or check.get("status") != "fail":
                            continue
                        message = str(check.get("message") or check.get("name") or "未说明原因").strip()
                        failed_reasons.append(f"{agent_id}: {message}")
                        break
            detail = "；".join(failed_reasons[:3])
            message = (
                "OpenCode 没有真正产出最终 index.html，或最后仍回退到了本地兜底页。"
                " 当前这次生成必须失败，不能把占位路径或兜底页当成功结果返回。"
            )
            if summary:
                message = f"{message} 验收摘要：{summary}"
            if detail:
                message = f"{message}；{detail}"
            raise RuntimeError(message)

        validation_layers = execution_report.get("validation_layers", [])
        if isinstance(validation_layers, list):
            blocking_failed = [
                layer for layer in validation_layers
                if isinstance(layer, dict) and layer.get("blocking") and layer.get("status") == "failed"
            ]
            if not blocking_failed:
                return
        failed_reasons: list[str] = []
        if isinstance(results, dict):
            for agent_id, result in results.items():
                if not isinstance(result, dict) or result.get("status") != "failed":
                    continue
                checks = result.get("checks", [])
                if not isinstance(checks, list):
                    continue
                for check in checks:
                    if not isinstance(check, dict) or check.get("status") != "fail":
                        continue
                    message = str(check.get("message") or check.get("name") or "未说明原因").strip()
                    failed_reasons.append(f"{agent_id}: {message}")
                    break

        detail = "；".join(failed_reasons[:3])
        message = f"{summary}；{detail}" if detail else summary
        self._emit(emit, f"执行层发现问题（已放行）：{message}", "execution-orchestrator", "warning")
        # 不再阻止返回，让页面继续生成

    @staticmethod
    def _preflight_generation_readiness(spec: dict[str, Any]) -> None:
        if spec.get("activity_type") != "music_game":
            return
        music_logic_contract = spec.get("music_logic_contract", {}) if isinstance(spec.get("music_logic_contract"), dict) else {}
        playable_game = spec.get("music_game", {}).get("playable_game", {}) if isinstance(spec.get("music_game"), dict) else {}
        errors = validate_music_logic_contract(
            music_logic_contract,
            playable_game if isinstance(playable_game, dict) else None,
        )
        readiness_errors = list(errors)
        if not isinstance(playable_game, dict) or not playable_game:
            readiness_errors.append("缺少 playable_game。")
        else:
            if not playable_game.get("materials"):
                readiness_errors.append("playable_game.materials 不能为空。")
            if not playable_game.get("target_sequence"):
                readiness_errors.append("playable_game.target_sequence 不能为空。")
            if not playable_game.get("required_student_actions"):
                readiness_errors.append("playable_game.required_student_actions 不能为空。")
            if not str(playable_game.get("completion_condition") or "").strip():
                readiness_errors.append("playable_game.completion_condition 不能为空。")
        if readiness_errors:
            detail = "；".join(dict.fromkeys(str(item) for item in readiness_errors if str(item).strip()))
            raise RuntimeError(f"生成前检查未通过：{detail}")

    @staticmethod
    def _can_retry_current_artifact(execution_report: dict[str, Any]) -> bool:
        results = execution_report.get("results", {}) if isinstance(execution_report.get("results"), dict) else {}
        failed_agents = {
            str(agent_id)
            for agent_id, result in results.items()
            if isinstance(result, dict) and result.get("status") == "failed"
        }
        if not failed_agents:
            return False
        page_layer_agents = {
            "frontend_artifact_builder",
            "browser_qa_agent",
            "code_interpreter",
        }
        return failed_agents.issubset(page_layer_agents)
