"""pytest 全局 fixtures：路径注入、鉴权 token、用户数据准备与清理。"""
import os
import sys

# 把项目根加入 sys.path，保证 `from common.xxx` / `from apis.xxx` 可正常导入
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from common.logger import logger
from apis.auth_api import AuthApi
from apis.user_api import UserApi
from utils.data_utils import gen_user, unique_phone


# ---------------- 数据准备类 ----------------

@pytest.fixture
def unique_user():
    """生成唯一用户数据（未注册），供注册类用例使用。"""
    return gen_user()


@pytest.fixture
def registered_user(unique_user):
    """注册一个用户并返回其数据，供登录类用例使用。"""
    resp = AuthApi().register(**unique_user)
    assert resp.status_code == 201
    return unique_user


# ---------------- 鉴权类（session 级，非 autouse） ----------------

@pytest.fixture(scope="session")
def operator_token():
    """全会话共用的登录 token。非 autouse，登录链路异常不会拖垮全部用例。"""
    user = gen_user(fullName="操作员", city="上海")
    resp = AuthApi().register(**user).json()
    assert resp["code"] == 0, f"操作员注册失败：{resp}"
    return resp["data"]["token"]


@pytest.fixture(scope="session")
def operator_user_id(operator_token):
    """当前操作员的用户 ID（用于「不能删除自己」用例）。"""
    resp = AuthApi(token=operator_token).profile().json()
    assert resp["code"] == 0
    return resp["data"]["id"]


# ---------------- API 实例 ----------------

@pytest.fixture
def auth_api(operator_token):
    return AuthApi(token=operator_token)


@pytest.fixture
def user_api(operator_token):
    return UserApi(token=operator_token)


# ---------------- 业务数据（自动清理） ----------------

@pytest.fixture
def created_user_id(user_api):
    """为每个用例新建一个用户，用例结束后自动删除。"""
    resp = user_api.create(
        fullName="待操作用户", phone=unique_phone(), city="广州"
    ).json()
    assert resp["code"] == 0, f"创建测试用户失败：{resp}"
    uid = resp["data"]["id"]
    yield uid
    # 清理：忽略删除失败（用例可能已删除）
    try:
        user_api.remove(uid)
    except Exception:
        pass


# ---------------- 通用日志 ----------------

@pytest.fixture(autouse=True)
def _log_case(request):
    logger.info(f"===== 开始：{request.node.nodeid} =====")
    yield
    logger.info(f"===== 结束：{request.node.nodeid} =====")
