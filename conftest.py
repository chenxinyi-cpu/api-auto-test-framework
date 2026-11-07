import pytest

from common.request_util import HttpRequest
from common.yaml_util import read_yaml

env_config=read_yaml("config/env.yaml")
current_env=env_config["current_env"]
BASE_URL=env_config[current_env]["base_url"]

@pytest.fixture(scope="session")
def http_client():
    client = HttpRequest(BASE_URL)
    yield client


@pytest.fixture(scope="session")
def login_token(http_client):
    login_data = {"username":"admin","password":"123456"}
    resp= http_client.send("POST","/api/login",json=login_data)

    assert resp.status_code == 200,f"登录HTTP失败：{resp.status_code}"
    body=resp.json()
    assert body["code"] == 200,f"登录业务失败：{body}"

    token = body["data"]["token"]
    http_client.set_token(token)

    yield token


