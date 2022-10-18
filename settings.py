import os
from loguru import logger

# 版本
VERSION = "0.1.0"

# 项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# redis
REDIS_HOST = "192.168.1.233"
REDIS_PORT = 6379
REDIS_PASSWORD = "123456andy"
REDIS_DB = 15

# 代理池名
POOL_NAME = "PROXY_POOL"

# web用户验证
WEB_USERNAME = "andy"
WEB_PASSWORD = "123456"








