"""认证模块接口封装：健康检查、注册、登录、获取当前用户。"""
from apis.base_api import BaseApi


class AuthApi(BaseApi):
    # 健康检查（公开）
    def health(self):
        return self.request("GET", "/api/health")

    # 注册（公开）；参数均可缺省，用于测试后端字段校验
    def register(self, username=None, password=None, fullName=None, phone=None, city=None):
        body = {}
        for k, v in (
            ("username", username), ("password", password),
            ("fullName", fullName), ("phone", phone), ("city", city),
        ):
            if v is not None:
                body[k] = v
        return self.request("POST", "/api/auth/register", json=body)

    # 登录（公开）
    def login(self, username, password):
        return self.request(
            "POST", "/api/auth/login",
            json={"username": username, "password": password},
        )

    # 获取当前登录用户（需鉴权）
    def profile(self):
        return self.request("GET", "/api/auth/profile")
