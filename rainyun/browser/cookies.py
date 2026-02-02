"""Cookies 读写。"""

import json
import logging
import os
import time

from selenium.webdriver.chrome.webdriver import WebDriver

from rainyun.config import Config
from rainyun.browser.urls import build_app_url

logger = logging.getLogger(__name__)


def _user_prefix(config: Config) -> str:
    user = config.display_name or config.rainyun_user
    return f"用户 {user} " if user else ""


def save_cookies(driver: WebDriver, config: Config) -> None:
    """保存 cookies 到文件。"""
    prefix = _user_prefix(config)
    cookies = driver.get_cookies()
    cookie_dir = os.path.dirname(config.cookie_file)
    if cookie_dir:
        os.makedirs(cookie_dir, exist_ok=True)
    with open(config.cookie_file, "w") as f:
        json.dump(cookies, f)
    logger.info(f"{prefix}Cookies 已保存到 {config.cookie_file}")


def load_cookies(driver: WebDriver, config: Config) -> bool:
    """从文件加载 cookies。"""
    prefix = _user_prefix(config)
    if not os.path.exists(config.cookie_file):
        logger.info(f"{prefix}未找到 cookies 文件")
        return False
    try:
        with open(config.cookie_file, "r") as f:
            cookies = json.load(f)
        # 先访问域名以便设置 cookie
        driver.get(build_app_url(config, "/"))
        for cookie in cookies:
            # 移除可能导致问题的字段
            cookie.pop("sameSite", None)
            cookie.pop("expiry", None)
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"{prefix}添加 cookie 失败: {e}")
        logger.info(f"{prefix}Cookies 已加载")
        return True
    except json.JSONDecodeError as e:
        backup_path = f"{config.cookie_file}.bad-{time.strftime('%Y%m%d-%H%M%S')}"
        try:
            os.replace(config.cookie_file, backup_path)
            logger.warning(f"{prefix}Cookies 文件损坏，已备份到 {backup_path}")
        except OSError as rename_error:
            logger.warning(f"{prefix}备份 cookies 文件失败: {rename_error}")
        try:
            with open(config.cookie_file, "w") as f:
                json.dump([], f)
            logger.info(f"{prefix}Cookies 文件已清空")
        except OSError as write_error:
            logger.warning(f"{prefix}清空 cookies 文件失败: {write_error}")
        logger.error(f"{prefix}加载 cookies 失败: {e}")
        return False
    except Exception as e:
        logger.error(f"{prefix}加载 cookies 失败: {e}")
        return False
