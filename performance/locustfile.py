from locust import HttpUser,between,task
import random



class LoginUser(HttpUser):
    wait_time = between(1,2)
    host = "http://127.0.0.1:8000"

    def on_start(self):
        resp = self.client.post(
            "/api/login",
            json={"username":"admin","password":"123456"},
            name="on_start_login"
        )
        if resp.status_code != 200 or resp.json().get("code") != 200:
            raise RuntimeError(f"登录失败：{resp.status_code}{resp.json()}")
        self.token=resp.json()["data"]["token"]

    @task(3)
    def login_correct(self):
        self.client.post(
            "/api/login",
            json={"username":"admin","password":"123456"},
            name="login_correct",
        )

    @task(1)
    def login_wrong_password(self):
        self.client.post(
            "/api/login",
            json={"username":"admin","password":"1234"},
            name="login_wrong_password",
        )

    @task(1)
    def get_user_with_token(self):
        self.client.get(
            "/api/user/1",
            headers={"Authorization":f"Bearer {self.token}"},
            name="get_user_with_token",
        )