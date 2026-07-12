from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app


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


if __name__ == "__main__":
    unittest.main()
