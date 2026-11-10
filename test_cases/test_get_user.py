import allure
import pytest
from common.yaml_util import read_yaml

cases = read_yaml("cases/get_user_case.yaml")
smoke_cases = [case for case in cases if case.get("smoke") is True]
normal_cases = [case for case in cases if case.get("smoke") is not True]

def _run_get_user_case(client,case):
    allure.dynamic.title(f"{case['case_id']} - {case['title']}")
    resp = client.send(
        method=case["method"],
        path=case["path"],
    )

    assert resp.status_code == case["expect_http"],(
        f"[{case['case_id']}]HTTP状态码不符："
        f"期望{case['expect_http']},实际是{resp.status_code}，body={resp.text}"
    )

    if case.get("expect_code") is not None:
        body = resp.json()
        assert body["code"] == case["expect_code"],(
            f"[{case['case_id']}]业务code不符："
            f"期望{case['expect_code']},实际为{body['code']}，body={body}"
        )
        if case.get("expect_msg") :
            assert case["expect_msg"] in body.get("msg",""),(
                f"[{case['case_id']}]msg不符："
                f"期望包括'{case['expect_msg']}',实际'{body.get('msg')}'"
            )


@allure.feature("用户查询接口")
@allure.story("冒烟-正常查询")
@pytest.mark.smoke
@pytest.mark.parametrize("case",smoke_cases,ids=[case["case_id"] for case in smoke_cases])
def test_get_user_smoke(http_client, login_token, case):
    _run_get_user_case(http_client, case)

@allure.feature("用户查询接口")
@allure.story("异常与边界")
@pytest.mark.parametrize("case",normal_cases,ids=[case["case_id"] for case in normal_cases])
def test_get_user_normal(http_client, login_token, case):
    _run_get_user_case(http_client, case)

