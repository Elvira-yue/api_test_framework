"""接口封装基类：统一请求入口与响应断言辅助方法。"""
import allure
from common.request_handler import http
from common.logger import logger


class BaseApi:
    """所有 API 类的父类，子类只需定义各接口方法。"""

    def __init__(self, token: str = None):
        self.token = token

    def request(self, method: str, path: str, **kwargs):
        """统一请求入口，自动携带 token。"""
        kwargs["auth_token"] = self.token
        with allure.step(f"{method.upper()} {path}"):
            return http.send(method, path, **kwargs)

    # ---------- 响应统一断言辅助 ----------
    @staticmethod
    def assert_ok(resp, expected_code: int = 0, msg: str = ""):
        """断言业务成功（code == expected_code）。"""
        body = resp.json()
        assert body["code"] == expected_code, f"{msg}code 不符：期望 {expected_code}，实际 {body['code']}，message={body.get('message')}"
        return body

    @staticmethod
    def assert_fail(resp, expected_code: int, msg: str = ""):
        """断言业务失败并校验 code。"""
        body = resp.json()
        assert body["code"] == expected_code, f"{msg}code 不符：期望 {expected_code}，实际 {body['code']}"
        return body

    @staticmethod
    def data(body):
        """取 data 字段，调用方做进一步断言。"""
        return body.get("data")
