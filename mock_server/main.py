from fastapi import FastAPI, HTTPException, Header, Depends
import uvicorn
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mock_server.models import LoginRequest, UpdateUserRequest


app = FastAPI(title="Mock User API")

USERS={
    1:{"user_id": 1, "username": "admin", "password": "123456", "email": "admin@test.com"},
    2: {"user_id": 2, "username": "alice", "password": "abcdef", "email": "alice@test.com"},
}
VALID_TOKENS = {"mock-token-abc123"}

security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="缺少Authorization请求头")

    # HTTPBearer 会自动把 Bearer 后面的 token 提取到 credentials.credentials 里
    token = credentials.credentials
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    return token


@app.post("/api/login")
async def login(body: LoginRequest):
    if body.username == "":
        return {"code":400,"msg":"用户名不能为空"}
    if body.password == "":
        return {"code":400,"msg":"密码不能为空"}
    if len(body.password) > 20:
        return {"code":400,"msg":"密码长度过长，最大为20"}
    for user in USERS.values():
        if user["username"] == body.username and user["password"] == body.password:
            return {"code":200,"msg":"success","data":{"token": "mock-token-abc123"}}
    return {"code":400,"msg":"账号或密码错误"}


@app.get("/api/user/{user_id}")
def get_user(user_id:int,token:str=Depends(verify_token)):
    if user_id not in USERS:
        raise HTTPException(status_code=404,detail="用户不存在")
    u = USERS[user_id]
    return {"code": 200, "msg": "success",
            "data": {"user_id": u["user_id"], "username": u["username"], "email": u["email"]}}

@app.put("/api/user/{user_id}")
def update_user(user_id:int,body:UpdateUserRequest,token:str=Depends(verify_token)):
    if user_id not in USERS:
        raise HTTPException(status_code=404,detail="用户不存在")
    USERS[user_id]["username"] = body.username
    return {"code": 200, "msg": "success", "data": {"user_id": user_id, "username": body.username}}


@app.delete("/api/user/{user_id}")
def delete_user(user_id:int,token:str=Depends(verify_token)):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="用户不存在")
    del USERS[user_id]
    return {"code": 200, "msg": "success"}




@app.get("/api/ping")
def ping():
    return {"msg": "pong"}

if __name__=="__main__":
    uvicorn.run("mock_server.main:app", host="127.0.0.1", port=8000, reload=True)