from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.game_workflow_orchestrator import build_lesson_game_workflow
from app.services.template_patch_command import apply_patch_command_to_workflow, build_patch_command

FIXTURE_DIR = ROOT / "frontend" / "tests" / "fixtures"

FIXTURES = {
    "lesson-meter-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "三拍子强弱拍，学生听到强拍进入。",
                "target_objective": "学生能听出三拍子的强弱弱，并在强拍进入。",
                "target_stage": "核心律动环节",
                "song_material": {},
            }
        }
    },
    "lesson-rhythm-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "节奏复刻：四分 休止 八分八分 切分。",
                "target_objective": "学生能听辨并拍回四分、休止、八分八分和切分节奏。",
                "target_stage": "核心节奏练习",
                "song_material": {
                    "song_title": "节奏练习",
                    "source": {"kind": "text_score"},
                    "phrases": [
                        {
                            "id": "phrase_1",
                            "label": "目标节奏",
                            "target_sequence": ["quarter", "rest", "eighth_pair", "syncopation"],
                        }
                    ],
                },
            }
        }
    },
    "lesson-pitch-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "旋律走向 do mi sol do_high。",
                "target_objective": "学生能听出 do mi sol do_high 的上行旋律路线。",
                "target_stage": "核心音高练习",
                "song_material": {
                    "song_title": "旋律练习",
                    "source": {"kind": "text_score"},
                    "phrases": [
                        {
                            "id": "phrase_1",
                            "label": "目标旋律",
                            "target_sequence": ["do", "mi", "sol", "do_high"],
                        }
                    ],
                },
            }
        }
    },
    "lesson-timbre-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "比较笛子和二胡的音色，重点听气息感和弦鸣证据。",
                "target_objective": "学生能根据音色证据比较笛子和二胡。",
                "target_stage": "核心听辨环节",
                "song_material": {},
            }
        }
    },
    "lesson-form-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "听辨 ABA 曲式：A 段主题，B 段对比，A 段再现。",
                "target_objective": "学生能按 A B A 顺序辨认曲式结构。",
                "target_stage": "核心听赏环节",
                "song_material": {},
            }
        }
    },
    "lesson-composition-runtime-state.json": {
        "lesson_analysis": {
            "lesson_context": {
                "target_music_element": "宫商角徵羽五声音阶旋律创编，并至少使用 do re mi sol la。",
                "target_objective": "学生能用五声音阶素材完成短句创编。",
                "target_stage": "创编环节",
                "song_material": {},
            }
        }
    },
}


def _state_from_proposal(proposal: dict) -> dict:
    workflow = build_lesson_game_workflow(proposal)
    return _state_from_workflow(workflow)


def _state_from_workflow(workflow: dict) -> dict:
    state = {
        "workflow": workflow,
        "instance": workflow.get("instance", {}),
        "proposal_card": workflow.get("proposal_card", {}),
        "config": (workflow.get("instance", {}) or {}).get("config", {}),
        "template_id": (workflow.get("instance", {}) or {}).get("template_id", ""),
    }
    return state


def main() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for filename, proposal in FIXTURES.items():
        path = FIXTURE_DIR / filename
        path.write_text(json.dumps(_state_from_proposal(proposal), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rhythm_workflow = build_lesson_game_workflow(FIXTURES["lesson-rhythm-runtime-state.json"])
    rhythm_patch = build_patch_command(rhythm_workflow, "第二关节奏不对，改成四分 休止 八分八分。")
    patched_rhythm_workflow = apply_patch_command_to_workflow(rhythm_workflow, rhythm_patch)
    (FIXTURE_DIR / "lesson-rhythm-patched-runtime-state.json").write_text(
        json.dumps(_state_from_workflow(patched_rhythm_workflow), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pitch_workflow = build_lesson_game_workflow(FIXTURES["lesson-pitch-runtime-state.json"])
    pitch_patch = build_patch_command(pitch_workflow, "第二关音高不对，改成 do mi sol。")
    patched_pitch_workflow = apply_patch_command_to_workflow(pitch_workflow, pitch_patch)
    (FIXTURE_DIR / "lesson-pitch-patched-runtime-state.json").write_text(
        json.dumps(_state_from_workflow(patched_pitch_workflow), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    timbre_workflow = build_lesson_game_workflow(FIXTURES["lesson-timbre-runtime-state.json"])
    timbre_patch = build_patch_command(timbre_workflow, "改成笛子和二胡音色对比，重点听气息感和弦鸣。")
    patched_timbre_workflow = apply_patch_command_to_workflow(timbre_workflow, timbre_patch)
    (FIXTURE_DIR / "lesson-timbre-patched-runtime-state.json").write_text(
        json.dumps(_state_from_workflow(patched_timbre_workflow), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
