"""认证模块测试：健康检查、注册、登录、获取当前用户。"""
import allure
from apis.auth_api import AuthApi
from apis.base_api import BaseApi as B


@allure.feature("认证模块")
class TestAuth:

    # ---------- 健康检查 ----------
    @allure.story("健康检查")
    def test_health(self):
        resp = AuthApi().health()
        body = B.assert_ok(resp)
        assert body["data"]["status"] == "up"

    # ---------- 注册 ----------
    @allure.story("注册-成功")
    def test_register_success(self, unique_user):
        resp = AuthApi().register(**unique_user)
        body = B.assert_ok(resp, expected_code=0)
        assert resp.status_code == 201
        assert body["data"]["token"]
        assert body["data"]["user"]["username"] == unique_user["username"]

    @allure.story("注册-账号已存在(409)")
    def test_register_duplicate(self, unique_user):
        AuthApi().register(**unique_user)
        resp = AuthApi().register(**unique_user)
        B.assert_fail(resp, 409)

    @allure.story("注册-参数缺失(400)")
    def test_register_missing_field(self, unique_user):
        unique_user.pop("phone")
        resp = AuthApi().register(**unique_user)
        B.assert_fail(resp, 400)

    # ---------- 登录 ----------
    @allure.story("登录-成功")
    def test_login_success(self, registered_user):
        resp = AuthApi().login(
            registered_user["username"], registered_user["password"]
        )
        body = B.assert_ok(resp)
        assert body["data"]["token"]

    @allure.story("登录-密码错误(401)")
    def test_login_wrong_password(self, registered_user):
        resp = AuthApi().login(registered_user["username"], "wrongpass")
        B.assert_fail(resp, 401)

    @allure.story("登录-参数缺失(400)")
    def test_login_missing(self):
        resp = AuthApi().login("", "")
        B.assert_fail(resp, 400)

    # ---------- 获取当前用户 ----------
    @allure.story("获取当前用户-成功")
    def test_profile_success(self, auth_api):
        resp = auth_api.profile()
        body = B.assert_ok(resp)
        assert body["data"]["id"]

    @allure.story("获取当前用户-未登录(401)")
    def test_profile_no_token(self):
        resp = AuthApi().profile()  # 不传 token
        B.assert_fail(resp, 401)
