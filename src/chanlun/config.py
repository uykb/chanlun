# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Dict


def get_data_path() -> Path:
    """
    返回项目数据目录路径
    优先使用环境变量 CHANLUN_DATA_PATH，否则默认到仓库根目录下的 data/
    """
    env_path = os.getenv("CHANLUN_DATA_PATH", "")
    if env_path:
        p = Path(env_path).expanduser().resolve()
    else:
        p = Path(__file__).resolve().parents[2] / "data"
    if p.is_dir() is False:
        p.mkdir(parents=True, exist_ok=True)
    return p


# 网络代理配置
PROXY_HOST: str = os.getenv("CHANLUN_PROXY_HOST", "")
PROXY_PORT: str = os.getenv("CHANLUN_PROXY_PORT", "")

# 钉钉机器人配置（旧版，默认空，使用者可通过环境或数据库覆盖）
DINGDING_KEY_CURRENCY: Dict[str, str] = {
    "token": os.getenv("CHANLUN_DD_TOKEN", ""),
    "secret": os.getenv("CHANLUN_DD_SECRET", ""),
}

# 飞书应用配置（默认空）
FEISHU_KEYS: Dict[str, Dict[str, str]] = {
    "default": {
        "app_id": os.getenv("CHANLUN_FS_APP_ID", ""),
        "app_secret": os.getenv("CHANLUN_FS_APP_SECRET", ""),
    },
    "user_id": os.getenv("CHANLUN_FS_USER_ID", ""),
}

# Binance 交易 API（默认空）
BINANCE_APIKEY: str = os.getenv("BINANCE_APIKEY", "")
BINANCE_SECRET: str = os.getenv("BINANCE_SECRET", "")
