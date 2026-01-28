import importlib.util
import unittest
from dataclasses import replace
from unittest.mock import patch

REQUESTS_AVAILABLE = importlib.util.find_spec("requests") is not None

if REQUESTS_AVAILABLE:
    import requests

    from rainyun.api.client import RainyunAPI, RainyunAPIError
    from rainyun.config import get_default_config


    class DummyResponse:
        def __init__(self, status_code: int, payload: dict, text: str = "") -> None:
            self.status_code = status_code
            self._payload = payload
            self.text = text

        def json(self) -> dict:
            return self._payload

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError("http error")


@unittest.skipUnless(REQUESTS_AVAILABLE, "requests 未安装，跳过 API 客户端测试")
class ApiClientTests(unittest.TestCase):
    def test_get_user_points_uses_base_url(self):
        config = replace(get_default_config(), api_base_url="http://example.com")
        api = RainyunAPI("key", config=config)
        response = DummyResponse(200, {"code": 200, "data": {"Points": 123}})
        with patch("rainyun.api.client.requests.get", return_value=response) as mock_get:
            points = api.get_user_points()

        self.assertEqual(points, 123)
        called_url = mock_get.call_args[0][0]
        self.assertEqual(called_url, "http://example.com/user/")

    def test_api_error_raises(self):
        api = RainyunAPI("key", config=get_default_config())
        response = DummyResponse(200, {"code": 70007, "message": "bad"})
        with patch("rainyun.api.client.requests.get", return_value=response):
            with self.assertRaises(RainyunAPIError):
                api.get_user_points()


if __name__ == "__main__":
    unittest.main()
