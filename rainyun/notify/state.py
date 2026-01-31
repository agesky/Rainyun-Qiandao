"""通知配置状态管理。"""

from contextlib import contextmanager
from threading import Lock

from rainyun.config import Config, DEFAULT_PUSH_CONFIG, get_default_config

push_config = DEFAULT_PUSH_CONFIG.copy()
_config_loaded = False
_skip_push_title = ""
_notify_channels: list[dict] = []
_config_lock = Lock()


def configure(config: Config) -> None:
    global _config_loaded, _skip_push_title, _notify_channels
    push_config.clear()
    push_config.update(config.push_config)
    _skip_push_title = config.skip_push_title
    raw_channels = getattr(config, "notify_channels", None)
    if isinstance(raw_channels, list):
        _notify_channels = [dict(item) for item in raw_channels if isinstance(item, dict)]
    else:
        _notify_channels = []
    _config_loaded = True


def ensure_loaded() -> None:
    if not _config_loaded:
        configure(get_default_config())


def apply_overrides(overrides: dict, ignore_default_config: bool) -> None:
    if not overrides:
        return
    if ignore_default_config:
        push_config.clear()
        push_config.update(overrides)
    else:
        push_config.update(overrides)


def get_skip_title() -> str:
    return _skip_push_title


def get_channels() -> list[dict]:
    return list(_notify_channels)


@contextmanager
def use_temp_config(overrides: dict, ignore_default_config: bool = True):
    with _config_lock:
        backup = push_config.copy()
        apply_overrides(overrides, ignore_default_config)
        try:
            yield
        finally:
            push_config.clear()
            push_config.update(backup)
