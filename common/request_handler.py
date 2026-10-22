"""requests 统一封装：会话复用、自动鉴权、日志记录、统一响应处理。"""
import requests
from common.config import config
from common.logger import logger


class RequestHandler:
    """HTTP 请求处理器，所有接口调用的底层入口。"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = config.base_url
        self.timeout = config.timeout

    def _build_url(self, url: str) -> str:
        if url.startswith("http"):
            return url
        return self.base_url + url

    def send(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        发送请求。
        kwargs 支持：headers / params / json / data / files / auth_token 等。
        若传入 auth_token，自动添加 Authorization: Bearer <token> 头。
        """
        final_url = self._build_url(url)
        headers = kwargs.pop("headers", {}) or {}

        # 自动注入鉴权头
        token = kwargs.pop("auth_token", None)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Content-Type", "application/json")

        kwargs.setdefault("timeout", self.timeout)

        # 记录请求日志
        logger.info(f"→ {method.upper()} {final_url}")
        for key in ("json", "params", "data"):
            if kwargs.get(key):
                logger.debug(f"  {key}: {kwargs[key]}")

        try:
            resp = self.session.request(method, final_url, headers=headers, **kwargs)
        except requests.RequestException as e:
            logger.error(f"  请求异常：{e}")
            raise

        logger.info(f"← HTTP {resp.status_code} ({resp.elapsed.total_seconds():.3f}s)")
        logger.debug(f"  body: {resp.text[:500]}")
        return resp

    # 便捷方法
    def get(self, url, **kw):
        return self.send("GET", url, **kw)

    def post(self, url, **kw):
        return self.send("POST", url, **kw)

    def put(self, url, **kw):
        return self.send("PUT", url, **kw)

    def delete(self, url, **kw):
        return self.send("DELETE", url, **kw)


# 全局单例
http = RequestHandler()
