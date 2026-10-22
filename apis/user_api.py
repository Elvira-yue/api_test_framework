"""用户管理模块接口封装：列表、详情、新增、修改、删除。"""
from apis.base_api import BaseApi


class UserApi(BaseApi):
    # 用户列表（分页 + 搜索）
    def list(self, page=1, pageSize=10, keyword=None):
        params = {"page": page, "pageSize": pageSize}
        if keyword:
            params["keyword"] = keyword
        return self.request("GET", "/api/users", params=params)

    # 用户详情
    def detail(self, user_id):
        return self.request("GET", f"/api/users/{user_id}")

    # 新增用户
    def create(self, fullName, phone, city, username=None, password=None):
        body = {"fullName": fullName, "phone": phone, "city": city}
        if username:
            body["username"] = username
        if password:
            body["password"] = password
        return self.request("POST", "/api/users", json=body)

    # 修改用户
    def update(self, user_id, fullName=None, phone=None, city=None):
        body = {}
        if fullName is not None:
            body["fullName"] = fullName
        if phone is not None:
            body["phone"] = phone
        if city is not None:
            body["city"] = city
        return self.request("PUT", f"/api/users/{user_id}", json=body)

    # 删除用户
    def remove(self, user_id):
        return self.request("DELETE", f"/api/users/{user_id}")
