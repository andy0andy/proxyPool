from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from typing import Optional, List
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import base64

from proxyPool import ProxyPool
from settings import *


"""
接口服务
1. 获取代理接口
2. 代理总量接口
3. 随机代理接口

"""

app = FastAPI(title="代理池服务", description="代理池对外接口")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pool = ProxyPool(redis_host=REDIS_HOST, redis_port=REDIS_PORT, redis_password=REDIS_PASSWORD, redis_db=REDIS_DB,
                 pool_name=POOL_NAME)


class User(BaseModel):
    username: Optional[str] = WEB_USERNAME
    password: Optional[str] = WEB_PASSWORD

@app.post("/token", description="用户验证")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if username == WEB_USERNAME and password == WEB_PASSWORD:
        return {
            "access_token": base64.b64encode(f"{username}:{password}".encode()).decode(),
            "token_type": "bearer"
        }
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码不正确")


@app.get("/proxies", description="获取代理接口")
def proxies(size: Optional[int] = 1, token: str = Depends(oauth2_scheme)) -> Optional[List[str]]:
    proxy_list = pool.query(size)
    return proxy_list


@app.get("/count", description="代理总量接口")
def count(token: str = Depends(oauth2_scheme)) -> int:
    total = pool.count()

    return total


@app.get("/random", description="随机代理接口")
def random(token: str = Depends(oauth2_scheme)) -> str:
    server = pool.random()

    return server


def runserver():
    uvicorn.run(app, host="0.0.0.0", port=8081, access_log=False)

if __name__ == '__main__':
    runserver()

    ...
