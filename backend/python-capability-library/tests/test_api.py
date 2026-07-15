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
        self.assertEqual(payload["data"]["activity_runtime"]["schemaVersion"], "activity-runtime.v1")
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
        self.assertEqual(set(ALLOWED_ACTIVITIES), set(ACTIVITY_INTERACTION_REGISTRY))
        for activity_id, interaction in ACTIVITY_INTERACTION_REGISTRY.items():
            self.assertIn(interaction["renderer"], SUPPORTED_RENDERERS)
            bundle = build_runtime_bundle(activity_id=activity_id, composition=None, request=None)
            self.assertEqual(bundle["activity_runtime"]["renderer"], interaction["renderer"])
            self.assertNotEqual(bundle["activity_runtime"]["renderer"], "completion")

    def test_new_activity_runtime_contracts(self) -> None:
        singing = build_runtime_bundle(activity_id="phrase_singing_practice", composition=None, request=None)
        timbre = build_runtime_bundle(activity_id="instrument_timbre_match", composition=None, request=None)
        self.assertEqual(singing["activity_runtime"]["renderer"], "singing-practice")
        self.assertIn("phrases", singing["activity_runtime"]["props"])
        self.assertEqual(timbre["activity_runtime"]["renderer"], "timbre-match")
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
        self.assertEqual(payload["nodes"][0]["activity_runtime"]["renderer"], "rhythm-drag")

    @patch("app.services.orchestration.package_design_agent._call_model")
    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_uses_ecnu_agent(self, ecnu_config, doubao_config, call_model) -> None:
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

        response = self.client.post("/api/v1/packages/design", json={
            "lesson": {"course_name": "节奏创编课"},
            "preferences": {"duration": 40},
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["schema_version"], "package-design.v1")
        self.assertEqual(data["design"]["provider"], "chat_ecnu")
        self.assertEqual(data["design"]["model"], "ecnu-max")
        self.assertEqual(data["design"]["workflow_engine"], "langgraph")
        self.assertIn("package_design_model", data["design"]["tool_calls"])
        self.assertIn("validate_package_design", data["design"]["tool_calls"])
        self.assertEqual(len(data["steps"]), 4)
        self.assertEqual(data["steps"][1]["activity_id"], "steady_beat_walk")

    @patch("app.services.orchestration.package_design_agent._call_model")
    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_retries_next_provider_after_validation_failure(
        self, ecnu_config, doubao_config, call_model
    ) -> None:
        ecnu_config.return_value = {
            "provider": "chat_ecnu", "enabled": True, "model": "ecnu-max",
            "api_key": "test", "url": "https://example.test",
        }
        doubao_config.return_value = {
            "provider": "doubao", "enabled": True, "model": "doubao-test",
            "api_key": "test", "base_url": "https://example.test",
        }
        call_model.side_effect = [
            {"steps": []},
            {"steps": [
                {"activity_id": "lesson_opening_hook"},
                {"activity_id": "steady_beat_walk"},
                {"activity_id": "exit_ticket_review"},
            ]},
        ]

        response = self.client.post("/api/v1/packages/design", json={
            "lesson": {"course_name": "节拍课"},
            "preferences": {},
        })

        self.assertEqual(response.status_code, 200)
        design = response.json()["data"]["design"]
        self.assertEqual(design["provider"], "doubao")
        self.assertEqual(call_model.call_count, 2)
        self.assertIn("chat_ecnu: model must return 3 to 7 steps", design["fallback_reason"])
        self.assertIn("provider:chat_ecnu:invalid", design["workflow_steps"])
        self.assertIn("provider:doubao:validated", design["workflow_steps"])

    @patch("app.services.orchestration.package_design_agent._doubao_config")
    @patch("app.services.orchestration.package_design_agent._ecnu_config")
    def test_package_design_has_explicit_rule_fallback(self, ecnu_config, doubao_config) -> None:
        ecnu_config.return_value = {"provider": "chat_ecnu", "enabled": False, "model": "ecnu-max"}
        doubao_config.return_value = {"provider": "doubao", "enabled": False, "model": ""}

        response = self.client.post("/api/v1/packages/design", json={
            "lesson": {"course_name": "节奏课", "music_elements": ["节拍"]},
            "preferences": {},
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["design"]["provider"], "rule_fallback")
        self.assertIn("chat_ecnu: not configured", data["design"]["fallback_reason"])
        self.assertEqual(data["design"]["workflow_engine"], "langgraph")
        self.assertIn("rule_package_design", data["design"]["tool_calls"])


if __name__ == "__main__":
    unittest.main()
