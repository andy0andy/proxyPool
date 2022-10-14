from fastapi import FastAPI
import uvicorn
from typing import Optional, List
from pydantic import BaseModel

from proxyPool import ProxyPool
from settings import *

"""
接口服务
1. 获取代理接口
2. 代理总量接口
3. 随机代理接口

"""

app = FastAPI(title="代理池服务", description="代理池对外接口")


class RedisConn(BaseModel):
    host: Optional[str] = REDIS_HOST
    port: Optional[int] = REDIS_PORT
    password: Optional[str] = REDIS_PASSWORD
    db: Optional[int] = REDIS_DB
    pool_name: Optional[str] = "PROXY_POOL"

@app.get("/proxys", description="获取代理接口")
def get_proxys(redis_conn: Optional[RedisConn] = None, size: Optional[int] = 1) -> Optional[List[str]]:
    proxyPool = ProxyPool(redis_host=redis_conn.host, redis_port=redis_conn.port, redis_password=redis_conn.password, redis_db=redis_conn.db, pool_name=redis_conn.pool_name)
    proxy_list = proxyPool.query(size)

    return proxy_list


@app.get("/count", description="代理总量接口")
def count(redis_conn: Optional[RedisConn] = None) -> int:
    proxyPool = ProxyPool(redis_host=redis_conn.host, redis_port=redis_conn.port, redis_password=redis_conn.password, redis_db=redis_conn.db, pool_name=redis_conn.pool_name)
    total = proxyPool.count()

    return total


@app.get("/random", description="随机代理接口")
def random(redis_conn: Optional[RedisConn] = None) -> str:
    print(f"{redis_conn=}")
    proxyPool = ProxyPool(redis_host=redis_conn.host, redis_port=redis_conn.port, redis_password=redis_conn.password, redis_db=redis_conn.db, pool_name=redis_conn.pool_name)
    server = proxyPool.random()

    return server


if __name__ == '__main__':
    uvicorn.run("web:app", debug=True, reload=True)
