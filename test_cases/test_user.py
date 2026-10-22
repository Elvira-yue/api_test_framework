"""用户管理模块测试：列表、详情、新增、修改、删除。"""
import allure
from apis.base_api import BaseApi as B
from utils.data_utils import unique_phone


@allure.feature("用户管理")
class TestUser:

    # ---------- 新增 ----------
    @allure.story("新增用户-成功")
    def test_create_user(self, user_api):
        resp = user_api.create(
            fullName="李四", phone=unique_phone(), city="北京"
        )
        body = B.assert_ok(resp)
        assert resp.status_code == 201
        assert body["data"]["fullName"] == "李四"

    @allure.story("新增用户-手机号非法(400)")
    def test_create_invalid_phone(self, user_api):
        resp = user_api.create(fullName="王五", phone="12345", city="成都")
        B.assert_fail(resp, 400)

    @allure.story("新增用户-手机号冲突(409)")
    def test_create_duplicate_phone(self, user_api, created_user_id):
        # 先查出已有用户手机号，再用同号新建
        detail = user_api.detail(created_user_id).json()
        phone = detail["data"]["phone"]
        resp = user_api.create(fullName="重复号", phone=phone, city="X")
        B.assert_fail(resp, 409)

    # ---------- 列表 ----------
    @allure.story("用户列表-分页")
    def test_list_users(self, user_api):
        resp = user_api.list(page=1, pageSize=10)
        body = B.assert_ok(resp)
        data = body["data"]
        assert isinstance(data["list"], list)
        assert data["page"] == 1
        assert data["pageSize"] == 10

    @allure.story("用户列表-关键字搜索")
    def test_list_with_keyword(self, user_api, created_user_id):
        detail = user_api.detail(created_user_id).json()
        name = detail["data"]["fullName"]
        resp = user_api.list(keyword=name)
        body = B.assert_ok(resp)
        ids = [u["id"] for u in body["data"]["list"]]
        assert created_user_id in ids

    # ---------- 详情 ----------
    @allure.story("用户详情-成功")
    def test_user_detail(self, user_api, created_user_id):
        resp = user_api.detail(created_user_id)
        body = B.assert_ok(resp)
        assert body["data"]["id"] == created_user_id

    @allure.story("用户详情-不存在(404)")
    def test_user_detail_not_found(self, user_api):
        resp = user_api.detail(999999)
        B.assert_fail(resp, 404)

    @allure.story("用户详情-ID非法(400)")
    def test_user_detail_invalid_id(self, user_api):
        resp = user_api.detail("abc")
        B.assert_fail(resp, 400)

    # ---------- 修改 ----------
    @allure.story("修改用户-成功")
    def test_update_user(self, user_api, created_user_id):
        resp = user_api.update(created_user_id, city="深圳")
        body = B.assert_ok(resp)
        assert body["data"]["city"] == "深圳"

    @allure.story("修改用户-不存在(404)")
    def test_update_not_found(self, user_api):
        resp = user_api.update(999999, city="X")
        B.assert_fail(resp, 404)

    # ---------- 删除 ----------
    @allure.story("删除用户-成功")
    def test_delete_user(self, user_api, created_user_id):
        resp = user_api.remove(created_user_id)
        B.assert_ok(resp)
        # 二次校验：详情应为 404
        detail = user_api.detail(created_user_id)
        B.assert_fail(detail, 404)

    @allure.story("删除用户-不能删除自己(400)")
    def test_delete_self(self, user_api, operator_user_id):
        resp = user_api.remove(operator_user_id)
        B.assert_fail(resp, 400)

    @allure.story("删除用户-不存在(404)")
    def test_delete_not_found(self, user_api):
        resp = user_api.remove(999999)
        B.assert_fail(resp, 404)
