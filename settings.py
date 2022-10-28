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

# 拨号命令
dial_start = "adsl-start"
dial_stop = "adsl-stop"

# 拨号间隔 s; 拨号一次大概10-12s之间
dial_interval = 60

# 拨号次数阈值
dial_threshold = 100

# vps池, 以ssh方式连接拨号
vps_pool = [
    {
        "host": "114.104.147.42",
        "port": 20041,
        "user": "root",
        "password": "d19891c67070",
        "server_name": "hshan01",
        "out_port": "8889"
    },
]










