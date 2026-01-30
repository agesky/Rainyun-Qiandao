import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from rainyun.data.store import DataStore
from rainyun.web.app import create_app
from rainyun.web.deps import get_store


class WebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name) / "config.json"
        self.store = DataStore(data_path)
        self.store.load()

        app = create_app()
        app.dependency_overrides[get_store] = lambda: self.store
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _login(self) -> str:
        response = self.client.post("/api/login", json={"password": "abc123"})
        self.assertEqual(response.status_code, 200)
        token = response.json()["data"]["token"]
        return token

    def test_account_crud(self) -> None:
        token = self._login()
        headers = {"Authorization": f"Bearer {token}"}

        create = self.client.post(
            "/api/accounts",
            json={"name": "主账号", "username": "user", "password": "pwd"},
            headers=headers,
        )
        self.assertEqual(create.status_code, 200)
        account_id = create.json()["data"]["id"]

        listing = self.client.get("/api/accounts", headers=headers)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.json()["data"]), 1)

        detail = self.client.get(f"/api/accounts/{account_id}", headers=headers)
        self.assertEqual(detail.status_code, 200)

        delete = self.client.delete(f"/api/accounts/{account_id}", headers=headers)
        self.assertEqual(delete.status_code, 200)


if __name__ == "__main__":
    unittest.main()
