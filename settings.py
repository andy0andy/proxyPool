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
            "host": "114.104.147.16",
            "port": 20189,
            "user": "root",
            "password": "ZxHshan01",
            "name": "hshan01",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20093,
            "user": "root",
            "password": "ZxHshan02",
            "name": "hshan02",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20101,
            "user": "root",
            "password": "ZxHshan03",
            "name": "hshan03",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20107,
            "user": "root",
            "password": "ZxHshan04",
            "name": "hshan04",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20227,
            "user": "root",
            "password": "ZxHshan05",
            "name": "hshan05",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20229,
            "user": "root",
            "password": "ZxHshan06",
            "name": "hshan06",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20231,
            "user": "root",
            "password": "ZxHshan07",
            "name": "hshan07",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20241,
            "user": "root",
            "password": "ZxHshan08",
            "name": "hshan08",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20243,
            "user": "root",
            "password": "ZxHshan09",
            "name": "hshan09",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },
    {
            "host": "114.104.147.16",
            "port": 20245,
            "user": "root",
            "password": "ZxHshan10",
            "name": "hshan10",
            "out_port": "6256",
            "auth_user": "zxkj",
            "auth_pass": "Wlhrag11",
    },

]


# log
# logger.add("logs/{time}.log", rotation="200 MB", retention="7 days", enqueue=True)







