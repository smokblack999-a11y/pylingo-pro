import unittest

from app.main import app


class RemoteExecutionSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_run_endpoint_is_disabled(self):
        response = self.client.post(
            "/api/run",
            json={"code": "raise RuntimeError('user code executed')"},
        )
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.get_json()["code"], "CODE_EXECUTION_DISABLED")

    def test_run_endpoint_does_not_execute_payload(self):
        response = self.client.post(
            "/api/run",
            json={"code": "__import__('os').environ.clear()"},
        )
        self.assertEqual(response.status_code, 410)
        self.assertIn("sandbox", response.get_json()["error"].lower())


if __name__ == "__main__":
    unittest.main()
