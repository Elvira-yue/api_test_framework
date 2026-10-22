"""全局配置：读取 data/config.yaml，支持多环境切换。"""
import os
import yaml


class _Config:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(self.base_dir, "data", "config.yaml"), "r", encoding="utf-8") as f:
            self._cfg = yaml.safe_load(f) or {}

    @property
    def env(self) -> str:
        return self._cfg.get("env", "dev")

    @property
    def base_url(self) -> str:
        return self._cfg["base_url"][self.env]

    @property
    def timeout(self) -> int:
        return self._cfg.get("timeout", 15)

    @property
    def database(self) -> dict:
        return self._cfg.get("database", {})

    @property
    def default_user(self) -> dict:
        return self._cfg.get("default_user", {})

    @property
    def allure(self) -> dict:
        return self._cfg.get("allure", {})


config = _Config()
