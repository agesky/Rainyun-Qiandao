"""兼容层：保留旧的 server_manager 导入路径。"""

from rainyun.server.manager import ServerInfo, ServerManager

__all__ = ["ServerInfo", "ServerManager"]
