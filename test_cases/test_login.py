from common.yaml_util import read_yaml
import pytest
import allure

case_list= read_yaml("cases/login_case.yaml")
smoke_cases = [c for c in case_list if c.get("smoke") is True]
normal_cases = [c for c in case_list if c.get("smoke") is not True]


def _assert_fields_exist(payload,field_paths,case_id):
    for path in field_paths:
        current = payload
        for key in path.split("."):
            assert key in current, f"[{case_id}] 字段缺失: {path}(在 {key} 处)"
            current = current[key]
        assert current is not None, f"[{case_id}] 字段值为None: {path}"


def _run_login_case(client,case):
    allure.dynamic.title(f"{case['case_id']} - {case['title']}")
    resp = client.send(
        method=case["method"],
        path=case["path"],
        json=case["json"],
    )
    assert resp.status_code == case["expect_http"], \
        (f"[{case['case_id']}] HTTP状态码不符: "
         f"期望{case['expect_http']}, 实际{resp.status_code}, body={resp.text}")

    if case["expect_code"] is not None:
        body = resp.json()
        assert body["code"] == case["expect_code"], (
            f"[{case['case_id']}] 业务code不符: "
            f"期望{case['expect_code']}, 实际{body.get('code')}, body={body}"
        )
        if case.get("expect_msg"):
            assert case["expect_msg"] in body.get("msg", ""), (
                f"[{case['case_id']}] msg不符: "
                f"期望包含'{case['expect_msg']}', 实际'{body.get('msg')}'"
            )
        if case.get("expect_fields"):
            _assert_fields_exist(body, case["expect_fields"], case["case_id"])

@allure.feature("登录接口")
@allure.story("冒烟-正常登录")
@pytest.mark.smoke
@pytest.mark.parametrize("case",smoke_cases,ids=[case["case_id"] for case in smoke_cases])
def test_login_smoke(http_client, case):
    _run_login_case(http_client,case)


@allure.feature("登录接口")
@allure.story("异常与边界")
@pytest.mark.parametrize("case",normal_cases,ids=[case["case_id"] for case in normal_cases])
def test_login_normal(http_client, case):
    _run_login_case(http_client,case)


# @allure.feature("登录接口")
# @pytest.mark.parametrize("case",case_list,ids=[c["case_id"] for c in case_list])
# def test_login(http_client,case):
#     allure.dynamic.title(f"{case['case_id']} - {case['title']}")
#     resp= http_client.send(
#         method= case["method"],
#         path= case["path"],
#         json= case["json"],
#     )
#     assert resp.status_code == case["expect_http"],\
#         (f"[{case['case_id']}] HTTP状态码不符: "
#          f"期望{case['expect_http']}, 实际{resp.status_code}, body={resp.text}")
#
#     if case["expect_code"] is not None:
#         body = resp.json()
#         assert body["code"] == case["expect_code"], (
#             f"[{case['case_id']}] 业务code不符: "
#             f"期望{case['expect_code']}, 实际{body.get('code')}, body={body}"
#         )
#         if case.get("expect_msg"):
#             assert case["expect_msg"] in body.get("msg", ""), (
#                 f"[{case['case_id']}] msg不符: "
#                 f"期望包含'{case['expect_msg']}', 实际'{body.get('msg')}'"
#             )
#         if case.get("expect_fields"):
#             _assert_fields_exist(body, case["expect_fields"], case["case_id"])



