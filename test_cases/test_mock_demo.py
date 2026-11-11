import pytest
import responses
import requests
from common.request_util import HttpRequest

@responses.activate
def test_first_mock():
    responses.add(
        method=responses.GET,
        url="http://127.0.0.1:8000/api/user/1",
        json={"code":200,"data":{"user_id":1,"username":"chen"}},
        status=200,
    )

    resp = requests.get("http://127.0.0.1:8000/api/user/1")
    assert resp.json()["code"] == 200
    assert resp.json()["data"]["username"] == "chen"
    assert len(responses.calls) == 1
    assert "user/1" in responses.calls[0].request.url


@responses.activate
def test_login_with_mocked_backend():
    responses.add(
        method=responses.POST,
        url="http://127.0.0.1:8000/api/login",
        json={"code":200,"msg":"success","data":{"token":"fake-token"}},
        status=200,
    )

    resp = requests.post(
        "http://127.0.0.1:8000/api/login",
        json={"username":"admin","password":"123"},
    )

    assert resp.status_code == 200
    assert resp.json()["data"]["token"] == "fake-token"

    sent_body = responses.calls[0].request.body
    assert b"admin" in sent_body
    assert b"123" in sent_body


@responses.activate
def test_login_business_error_with_mocked_backend():
    """
    演示：Mock 业务失败场景（HTTP 200 + 业务 code 400），
    验证封装层不会因为业务失败而抛异常。
    """
    responses.add(
        method=responses.POST,
        url="http://127.0.0.1:8000/api/login",
        json={"code": 400, "msg": "用户名不能为空"},
        status=200,
    )

    client = HttpRequest("http://127.0.0.1:8000")
    resp = client.send("POST", "/api/login", json={"username": "", "password": "123456"})

    assert resp.status_code == 200
    assert resp.json()["code"] == 400
    assert "用户名不能为空" in resp.json()["msg"]



@responses.activate
def test_login_connection_error_with_mocked_backend():
    responses.add(
        method=responses.POST,
        url="http://127.0.0.1:8000/api/login",
        body=requests.exceptions.ConnectionError("mocked connection error"),
    )

    client = HttpRequest("http://127.0.0.1:8000")

    with pytest.raises(requests.exceptions.ConnectionError):
        resp = client.send(
            method="POST",
            path="/api/login",
            json={"username":"admin","password":"123456"},
        )




