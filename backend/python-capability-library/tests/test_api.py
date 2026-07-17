from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.activities.activity_interaction_registry import (
    ACTIVITY_INTERACTION_REGISTRY,
    SUPPORTED_RENDERERS,
    get_activity_interaction,
)
from app.services.orchestration.package_design_agent import ALLOWED_ACTIVITIES
from app.services.music_content.music_content_registry import (
    validate_and_resolve_music_content,
)
from app.services.runtime.runtime_api_service import build_runtime_bundle


class MusicCapabilityApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["status"], "ok")

    def test_meter_content_is_validated_and_resolved(self) -> None:
        normalized, resolved = validate_and_resolve_music_content(
            entity_id="strong_weak_beat_circle",
            raw={"meter_ids": ["meter_2_4", "meter_3_4"], "bpm": 76, "bars": 4},
        )
        self.assertEqual(normalized["meter_ids"], ["meter_2_4", "meter_3_4"])
        self.assertEqual(
            [item["signature"] for item in resolved["meters"]],
            ["2/4", "3/4"],
        )
        self.assertEqual(resolved["meters"][1]["accentPattern"], ["strong", "weak", "weak"])

    def test_unknown_meter_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown meter"):
            validate_and_resolve_music_content(
                entity_id="strong_weak_beat_circle",
                raw={"meter_ids": ["meter_7_8"]},
            )

    def test_full_music_element_chain_is_validated_and_resolved(self) -> None:
        normalized, resolved = validate_and_resolve_music_content(
            entity_id="graphic_score_create",
            raw={
                "meter_ids": ["meter_3_4"],
                "rhythm_pattern_ids": ["rhythm_titi_ta"],
                "form_ids": ["form_aba"],
                "dynamic_ids": ["dynamic_p", "dynamic_f"],
            },
        )
        self.assertEqual(normalized["rhythm_pattern_ids"], ["rhythm_titi_ta"])
        self.assertEqual(resolved["rhythm_patterns"][0]["tokens"], ["ti-ti", "ta"])
        self.assertEqual(resolved["forms"][0]["sections"], ["A", "B", "A"])
        self.assertEqual([item["symbol"] for item in resolved["dynamics"]], ["p", "f"])

        normalized, resolved = validate_and_resolve_music_content(
            entity_id="xylophone_creation",
            raw={
                "meter_ids": ["meter_2_4"],
                "pitch_set_ids": ["pitch_do_re_mi_sol_la"],
                "melody_phrase_ids": ["melody_arch"],
                "timbre_ids": ["timbre_xylophone"],
            },
        )
        self.assertEqual(resolved["pitch_sets"][0]["notes"], ["do", "re", "mi", "sol", "la"])
        self.assertEqual(resolved["melody_phrases"][0]["contour"], ["same", "up", "up", "down", "down"])
        self.assertEqual(resolved["timbres"][0]["instrument"], "xylophone")

    def test_toolkits(self) -> None:
        response = self.client.get("/api/v1/toolkits")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertGreater(payload["data"]["count"], 0)
        self.assertIsInstance(payload["data"]["items"], list)

    def test_runtime_build(self) -> None:
        response = self.client.post(
            "/api/v1/runtime/build",
            json={
                "activity_id": "phrase_singing_practice",
                "request": {
                    "available_materials": {
                        "lyrics_text": ["第一乐句", "第二乐句"],
                        "melody_phrase": ["do re mi", "mi re do"],
                        "audio_clip": "https://example.com/demo.mp3",
                    }
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["activity_id"], "phrase_singing_practice")
        self.assertEqual(payload["data"]["runtime"]["runtime_status"], "ready")
        self.assertEqual(payload["data"]["activity_runtime"]["schemaVersion"], "interactive-node-runtime.v2")
        self.assertEqual(payload["data"]["activity_runtime"]["family"], "phrase_singing")
        self.assertEqual(payload["data"]["activity_runtime"]["variant"], "whole_phrase")
        self.assertEqual(
            payload["data"]["runtime"]["student_game_state"]["config"]["activity_id"],
            "phrase_singing_practice",
        )

    def test_runtime_build_invalid_activity(self) -> None:
        response = self.client.post(
            "/api/v1/runtime/build",
            json={"activity_id": "not_exists"},
        )

        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "activity_not_found")

    def test_all_activities_have_supported_student_renderers(self) -> None:
        self.assertEqual(len(ACTIVITY_INTERACTION_REGISTRY), 33)
        reviewed = {
            activity_id for activity_id, spec in ACTIVITY_INTERACTION_REGISTRY.items()
            if spec.get("component_url")
        }
        self.assertEqual(set(ALLOWED_ACTIVITIES), reviewed)
        formal_renderers = [
            spec["renderer"] for spec in ACTIVITY_INTERACTION_REGISTRY.values()
        ]
        self.assertEqual(len(formal_renderers), len(set(formal_renderers)))
        component_urls = [
            spec["component_url"] for spec in ACTIVITY_INTERACTION_REGISTRY.values()
            if spec.get("component_url")
        ]
        self.assertEqual(len(component_urls), len(set(component_urls)))
        for activity_id, interaction in ACTIVITY_INTERACTION_REGISTRY.items():
            bundle = build_runtime_bundle(activity_id=activity_id, composition=None, request=None)
            self.assertEqual(bundle["activity_runtime"]["renderer"], interaction["renderer"])
            self.assertEqual(
                bundle["activity_runtime"]["legacyRenderer"],
                interaction["legacy_renderer"],
            )
            self.assertEqual(bundle["activity_runtime"]["nodeType"], "activity")
            self.assertTrue(bundle["activity_runtime"]["family"])
            self.assertTrue(bundle["activity_runtime"]["variant"])
            self.assertNotEqual(bundle["activity_runtime"]["renderer"], "completion")

    def test_new_activity_runtime_contracts(self) -> None:
        singing = build_runtime_bundle(activity_id="phrase_singing_practice", composition=None, request=None)
        timbre = build_runtime_bundle(activity_id="instrument_timbre_match", composition=None, request=None)
        self.assertEqual(singing["activity_runtime"]["renderer"], "activity:phrase_singing_practice")
        self.assertEqual(singing["activity_runtime"]["legacyRenderer"], "singing-practice")
        self.assertIn("phrases", singing["activity_runtime"]["props"])
        self.assertEqual(timbre["activity_runtime"]["renderer"], "activity:instrument_timbre_match")
        self.assertEqual(timbre["activity_runtime"]["legacyRenderer"], "timbre-match")
        self.assertIn("items", timbre["activity_runtime"]["props"])
        with self.assertRaises(ValueError):
            get_activity_interaction("activity_without_renderer")

    def test_rule_assessment_scores_actual_answer(self) -> None:
        response = self.client.post("/api/v1/assessments/grade", json={
            "activity_id": "solfege_sorting",
            "renderer": "solfege-sort",
            "result": {"sequence": ["do", "mi", "re", "sol"]},
            "assessment": {
                "mode": "rule",
                "answerKey": {"sequence": ["do", "re", "mi", "sol"]},
            },
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["score"], 50)
        self.assertEqual(data["provider"], "system")

    @patch("app.services.assessment.activity_assessment_service._doubao_config")
    @patch("app.services.assessment.activity_assessment_service._ecnu_config")
    def test_ai_assessment_has_explicit_fallback(self, ecnu_config, doubao_config) -> None:
        ecnu_config.return_value = {"provider": "chat_ecnu", "enabled": False}
        doubao_config.return_value = {"provider": "doubao", "enabled": False}
        response = self.client.post("/api/v1/assessments/grade", json={
            "activity_id": "xylophone_creation",
            "renderer": "virtual-instrument",
            "result": {"notes": ["do", "re", "mi", "sol"]},
            "assessment": {"mode": "ai", "rubric": []},
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["mode"], "ai_fallback")
        self.assertNotEqual(data["score"], 100)

    def test_package_build(self) -> None:
        response = self.client.post(
            "/api/v1/packages/build",
            json={"nodes": [{
                "client_ref": "node-1",
                "activity_id": "rhythm_question_answer",
                "composition": {"selected_node_type": "rhythm_game"},
            }]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()["data"]
        self.assertEqual(payload["schema_version"], "activity-package.v1")
        self.assertEqual(payload["nodes"][0]["client_ref"], "node-1")
        self.assertEqual(
            payload["nodes"][0]["activity_runtime"]["renderer"],
            "activity:rhythm_question_answer",
        )
        self.assertEqual(payload["nodes"][0]["activity_runtime"]["legacyRenderer"], "rhythm-drag")

    def test_game_is_a_formal_interactive_node(self) -> None:
        response = self.client.post("/api/v1/runtime/build", json={
            "activity_id": "rhythm_question_answer",
            "composition": {
                "interactive_node_type": "game",
                "selected_game_template": "rhythm_echo_core",
            },
            "request": {
                "game": {
                    "templateId": "rhythm_echo_core",
                    "prompt": "听完以后再模仿。",
                },
            },
        })
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["data"]["activity_runtime"]
        self.assertEqual(runtime["nodeType"], "game")
        self.assertEqual(runtime["variant"], "rhythm_echo_core")
        self.assertEqual(runtime["renderer"], "reviewed-game")
        self.assertEqual(
            runtime["componentUrl"],
            "/template-console/student-game.html?template=rhythm_echo_core&review=1",
        )
        self.assertEqual(
            runtime["props"]["studentGameState"]["template_id"],
            "rhythm_echo_core",
        )

    def test_virtual_instrument_task_has_objective_evidence_contract(self) -> None:
        response = self.client.post("/api/v1/runtime/build", json={
            "activity_id": "rhythm_warmup",
            "composition": {"interactive_node_type": "instrument_task"},
            "request": {
                "instrument_task": {
                    "kind": "steady_beat",
                    "instrumentId": "virtual_frame_drum",
                    "gradePreset": "middle_primary",
                    "bpm": 60,
                },
            },
        })
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["data"]["activity_runtime"]
        self.assertEqual(runtime["nodeType"], "instrument_task")
        self.assertEqual(runtime["variant"], "steady_beat")
        self.assertEqual(runtime["assessment"]["mode"], "instrument_evidence")

        assessment = self.client.post("/api/v1/assessments/grade", json={
            "activity_id": "rhythm_warmup",
            "renderer": "virtual-instrument",
            "result": {
                "events": [
                    {"timeMs": 0, "zoneId": "center"},
                    {"timeMs": 1000, "zoneId": "center"},
                    {"timeMs": 2000, "zoneId": "center"},
                    {"timeMs": 3000, "zoneId": "center"},
                ],
            },
            "assessment": runtime["assessment"],
        })
        self.assertEqual(assessment.status_code, 200)
        result = assessment.json()["data"]
        self.assertEqual(result["mode"], "instrument_evidence")
        self.assertEqual(result["score"], 100)

    def test_legacy_virtual_instrument_activity_gets_explicit_instrument(self) -> None:
        response = self.client.post("/api/v1/runtime/build", json={
            "activity_id": "xylophone_creation",
            "composition": {},
            "request": {},
        })
        self.assertEqual(response.status_code, 200)
        runtime = response.json()["data"]["activity_runtime"]
        self.assertEqual(runtime["legacyRenderer"], "virtual-instrument")
        self.assertEqual(runtime["props"]["instrumentId"], "virtual_xylophone")

    def test_constrained_piano_composition_accepts_rhythm_content(self) -> None:
        normalized, resolved = validate_and_resolve_music_content(
            entity_id="instrument_task:constrained_composition",
            raw={
                "meter_ids": ["meter_4_4"],
                "bpm": 80,
                "bars": 4,
                "rhythm_pattern_ids": ["rhythm_ta_ta"],
                "pitch_set_ids": ["pitch_do_re_mi"],
                "dynamic_ids": ["dynamic_p", "dynamic_f"],
            },
        )
        self.assertEqual(normalized["rhythm_pattern_ids"], ["rhythm_ta_ta"])
        self.assertIn("pitch_sets", resolved)

    @patch("app.services.orchestration.package_design_agent._call_model_messages")
    @patch("app.services.orchestration.package_design_agent._call_model")
    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_uses_ecnu_agent(
        self, ecnu_config, doubao_config, call_model, call_model_messages,
    ) -> None:
        ecnu_config.return_value = {
            "provider": "chat_ecnu", "enabled": True, "model": "ecnu-max",
            "api_key": "test", "url": "https://example.test",
        }
        doubao_config.return_value = {"provider": "doubao", "enabled": False, "model": ""}
        call_model.return_value = {
            "title": "节奏创编互动包",
            "reasoning_summary": "根据教学目标组织活动。",
            "steps": [
                {"activity_id": "lesson_opening_hook", "title": "听辨导入"},
                {"activity_id": "steady_beat_walk", "title": "稳定拍行走"},
                {"activity_id": "body_percussion_builder", "title": "身体打击乐创编"},
                {"activity_id": "exit_ticket_review", "title": "出口票"},
            ],
        }

        call_model_messages.return_value = {"passed": True, "score": 94, "issues": []}

        response = self.client.post("/api/v1/packages/design", json={
            "lesson": {"course_name": "节奏创编课"},
            "preferences": {"duration": 40},
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["schema_version"], "package-design.v1")
        self.assertEqual(data["design"]["provider"], "chat_ecnu")
        self.assertEqual(data["design"]["model"], "ecnu-max")
        self.assertEqual(len(data["steps"]), 4)
        self.assertEqual(data["steps"][1]["activity_id"], "steady_beat_walk")

    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_falls_back_to_rule_audit(self, ecnu_config, doubao_config) -> None:
        ecnu_config.return_value = {"provider": "chat_ecnu", "enabled": False, "model": "ecnu-max"}
        doubao_config.return_value = {"provider": "doubao", "enabled": False, "model": ""}

        response = self.client.post("/api/v1/packages/design", json={
            "lesson": {"course_name": "节奏课", "music_elements": ["节拍"]},
            "preferences": {},
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["quality_report"]["provider"], "rule_fallback")
        self.assertIn("not configured", data["quality_report"]["fallback_reason"])


    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_workflow_interrupts_for_teacher_review(
        self, ecnu_config, doubao_config,
    ) -> None:
        ecnu_config.return_value = {
            "provider": "chat_ecnu", "enabled": False, "model": "ecnu-max",
        }
        doubao_config.return_value = {
            "provider": "doubao", "enabled": False, "model": "",
        }

        started = self.client.post("/api/v1/packages/design/workflows", json={
            "lesson": {"course_name": "节奏课", "music_elements": ["节拍"]},
            "preferences": {},
            "quality_review_mode": "rules",
        })

        self.assertEqual(started.status_code, 200)
        workflow = started.json()["data"]
        self.assertEqual(workflow["status"], "awaiting_teacher_review")
        self.assertEqual(workflow["review"]["type"], "package_teacher_review")
        self.assertIn("package", workflow["review"])

        reviewed = self.client.post(
            f"/api/v1/packages/design/workflows/{workflow['workflow_id']}/review",
            json={"decision": "approve"},
        )

        self.assertEqual(reviewed.status_code, 200)
        completed = reviewed.json()["data"]
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(
            completed["package"]["teacher_review"]["decision"], "approve",
        )
        self.assertEqual(
            completed["package"]["design"]["orchestration"],
            "langgraph-stategraph",
        )

    @patch("app.services.orchestration.package_design_agent._call_model_messages")
    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_agent_revision_changes_only_requested_node(
        self, ecnu_config, doubao_config, call_model_messages,
    ) -> None:
        ecnu_config.return_value = {
            "provider": "chat_ecnu", "enabled": True, "model": "ecnu-max",
            "api_key": "test", "url": "https://example.test",
        }
        doubao_config.return_value = {
            "provider": "doubao", "enabled": False, "model": "",
        }
        call_model_messages.return_value = {
            "activity_id": "rhythm_question_answer",
            "title": "简化节奏模仿",
            "description": "先示范，再使用四张节奏卡完成模仿。",
            "difficulty": "easy",
            "rhythmCardCount": 4,
            "hintEnabled": True,
        }

        response = self.client.post("/api/v1/packages/design/nodes/revise", json={
            "lesson": {"grade": "三年级"},
            "node": {
                "activity_id": "rhythm_question_answer",
                "title": "节奏问答",
                "sort_order": 2,
            },
            "feedback": "降低难度，节奏卡改成四张并增加教师示范。",
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["node"]["activity_id"], "rhythm_question_answer")
        self.assertEqual(data["node"]["sort_order"], 2)
        self.assertEqual(data["node"]["rhythmCardCount"], 4)
        self.assertEqual(data["provider"], "chat_ecnu")


if __name__ == "__main__":
    unittest.main()
