import importlib.util
import time
import unittest
from dataclasses import replace
from unittest.mock import patch

REQUESTS_AVAILABLE = importlib.util.find_spec("requests") is not None

if REQUESTS_AVAILABLE:
    from rainyun.config import get_default_config
    from rainyun.server.manager import ServerManager


class DummyAPI:
    points = 0
    renew_price = 0
    server_title = "测试服务器"

    def __init__(self, api_key: str, config=None) -> None:
        self.renew_calls = []

    def get_user_points(self) -> int:
        return self.points

    def get_server_ids(self) -> list:
        return [101]

    def get_server_detail(self, server_id: int) -> dict:
        return {
            "Data": {
                "ExpDate": int(time.time()) + 3600,
                "EggType": {"egg": {"title": self.server_title}},
            },
            "RenewPointPrice": {"7": self.renew_price},
        }

    def renew_server(self, server_id: int, days: int = 7) -> dict:
        self.renew_calls.append((server_id, days))
        return {"ok": True}


@unittest.skipUnless(REQUESTS_AVAILABLE, "requests 未安装，跳过服务器管理测试")
class ServerManagerTests(unittest.TestCase):
    def test_auto_renew_success(self):
        DummyAPI.points = 1000
        DummyAPI.renew_price = 200
        config = replace(
            get_default_config(),
            auto_renew=True,
            renew_threshold_days=7,
            renew_product_ids=[],
            renew_product_ids_parse_error=False,
        )
        with patch("rainyun.server.manager.RainyunAPI", DummyAPI):
            manager = ServerManager("key", config=config)
            result = manager.check_and_renew()

        self.assertEqual(result["renewed"], [DummyAPI.server_title])
        self.assertTrue(result["servers"][0]["renewed"])
        self.assertEqual(manager.api.renew_calls, [(101, 7)])

    def test_points_warning(self):
        DummyAPI.points = 100
        DummyAPI.renew_price = 500
        config = replace(
            get_default_config(),
            auto_renew=False,
            renew_threshold_days=7,
            renew_product_ids=[],
            renew_product_ids_parse_error=False,
        )
        with patch("rainyun.server.manager.RainyunAPI", DummyAPI):
            manager = ServerManager("key", config=config)
            result = manager.check_and_renew()

        self.assertIsNotNone(result["points_warning"])
        self.assertEqual(result["points_warning"]["shortage"], 400)


if __name__ == "__main__":
    unittest.main()
