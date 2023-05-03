import os
from loguru import logger

# 版本
VERSION = "0.1.3"

# 项目根目录
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# redis
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = "123456"
REDIS_DB = 15

# 代理池名
POOL_NAME = "ProxyPool"

# web用户验证
WEB_USERNAME = "root"
WEB_PASSWORD = "123456"

# 拨号命令
dial_start = "adsl-start"
dial_stop = "adsl-stop"

# 拨号间隔 s; 拨号一次大概10-12s之间
dial_interval = 5

# 拨号次数阈值
dial_threshold = 100

# vps池, 以ssh方式连接拨号
vps_pool = [
    {
            "host": "vps ip",
            "port": "vps port",
            "user": "vps ssh 用户名",
            "password": "vps ssh 密码",
            "name": "展示名",
            "out_port": "vps 对外代理端口",
            "auth_user": "web 验证用户名",
            "auth_pass": "web 验证密码",
    },

]


# log
# logger.add("logs/{time}.log", rotation="200 MB", retention="7 days", enqueue=True)







