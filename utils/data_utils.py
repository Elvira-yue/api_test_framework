"""数据工具：读取 test_data.yaml + 动态生成唯一值（避免唯一键冲突）。"""
import os
import time
import yaml
from common.config import config


def load_yaml(path: str = "data/test_data.yaml") -> dict:
    full = os.path.join(config.base_dir, path)
    with open(full, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def unique_username(prefix: str = "u") -> str:
    """生成唯一用户名（3-20 位字母/数字/下划线）。"""
    return f"{prefix}{int(time.time() * 1000)}"[:20]


def unique_phone() -> str:
    """生成唯一的大陆手机号。"""
    ts = int(time.time() * 1000)
    return f"139{ts % 100000000:08d}"


def gen_user(**overrides) -> dict:
    """生成一个合法的用户注册数据，可通过 overrides 覆盖字段。"""
    base = {
        "username": unique_username(),
        "password": "123456",
        "fullName": "测试用户",
        "phone": unique_phone(),
        "city": "杭州",
    }
    base.update(overrides)
    return base
