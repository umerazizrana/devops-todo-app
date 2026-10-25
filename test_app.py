import unittest
from unittest.mock import patch

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DevOps Task Manager", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "healthy"})

    def test_invalid_titles_do_not_access_database(self):
        invalid_titles = ["", "   ", "x" * 201, None, 123]

        with patch("app.connect_db") as database:
            for title in invalid_titles:
                with self.subTest(title=title):
                    response = self.client.post(
                        "/api/tasks",
                        json={"title": title},
                    )
                    self.assertEqual(response.status_code, 400)

            database.assert_not_called()

    def test_missing_title(self):
        response = self.client.post("/api/tasks", json={})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_shape(self):
        response = self.client.post("/api/tasks", json=["a task"])
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
