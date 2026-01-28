"""兼容层：保留旧的 api_client 导入路径。"""

from rainyun.api.client import RainyunAPI, RainyunAPIError

__all__ = ["RainyunAPI", "RainyunAPIError"]
