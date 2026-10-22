"""日志封装：控制台 + 文件双输出。"""
import logging
import os
from datetime import datetime
from common.config import config


class _Logger:
    def __init__(self):
        self._logger = logging.getLogger("api_test")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()
        self._logger.propagate = False

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台输出
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        self._logger.addHandler(sh)

        # 文件输出
        log_dir = os.path.join(config.base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(
            os.path.join(log_dir, f"test_{datetime.now():%Y%m%d}.log"),
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        self._logger.addHandler(fh)

    @property
    def log(self) -> logging.Logger:
        return self._logger


logger = _Logger().log
