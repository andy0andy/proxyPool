import redis
from typing import Optional, List

from settings import *

"""
1. 池用redis的有序集合维护
2. 代理操作：
    1. 入库
    2. 查询
    3. 删除
    4. 随机代理（平均分配: 取最小分数的代理）
    
"""


class ProxyPool(object):
    # 代理权重增量
    weight = 1

    def __init__(self, redis_host: str = REDIS_HOST,
                 redis_port: int = REDIS_PORT,
                 redis_password: str = REDIS_PASSWORD,
                 redis_db: int = REDIS_DB,
                 pool_name: str = POOL_NAME):

        """
        初始化

        :param redis_host:
        :param redis_port:
        :param redis_password:
        :param redis_db:
        """

        self._redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)

        self.pool_name = pool_name

    def add(self, servers: List[str]):

        """
        添加多个代理
        :param servers: ["[ip]:[port]", ]
        :return:
        """

        if not servers:
            logger.warning(f"Missing argument.")
        else:
            for server in servers:
                code = self._redis.zadd(self.pool_name, {server: 0})
                if code != 1:
                    logger.warning(f"Add proxy fail.")
                    break

    def query(self, size: Optional[int] = -1, use_times: Optional[int] = -1) -> List[str]:
        """
        查询代理，返回代理列表
        :param size: 返回个数；-1：代表返回所有
        :param use_times: 权重，查找少于此权重的所有代理，-1：表示优先返回小权重代理
        :return:
        """

        proxy_list = []

        if use_times == 0:
            use_times = 0
        elif use_times == -1:
            use_times = "+inf"

        servers = self._redis.zrangebyscore(self.pool_name, 0, use_times)
        if size == -1:
            pass
        else:
            servers = servers[:size]

        for server in servers:
            server = server.decode()
            proxy_list.append(server)
            self._add_weight(server)

        return proxy_list


    def delete(self, server: Optional[str] = None, all: Optional[bool] = False):
        """
        删除指定代理
        :param all: 是否全部删除
        :param server: [ip]:[port]
        :return:
        """

        if all:
            self._redis.zremrangebyrank(self.pool_name, 0, -1)
        else:
            if not server:
                logger.warning(f"missing argument.")
            else:
                code = self._redis.zrem(self.pool_name, server)
                if code != 1:
                    logger.warning(f"del proxy: {server} fail.")

    def random(self):
        """
        随机返回代理
        :return:
        """

        servers = self._redis.zrangebylex(self.pool_name, "-", "+")
        server = servers[0].decode()
        self._add_weight(server)

        return server

    def count(self):
        """
        统计代理总量
        :return:
        """

        total = self._redis.zlexcount(self.pool_name, "-", "+")
        return total

    def _add_weight(self, server: str):
        """
        代理增加权重
        :param server: 代理
        :return:
        """

        score = self._redis.zscore(self.pool_name, server)
        if score is not None:
            score += self.weight
            self._redis.zadd(self.pool_name, {server: score})
        else:
            logger.warning(f"argument error.")

    def isExist(self, server):
        """
        判断有序集合是否含有此键
        :param server:
        :return:
        """

        ok = self._redis.zscore(self.pool_name, server)
        if ok is None:
            return False

        return True


    def gt_score_threshold(self, threshold: Optional[int] = dial_threshold):
        """
        大于拨号阈值的代理
        :param threshold:
        :return:
        """

        servers = self._redis.zrangebyscore(self.pool_name, threshold, 999999)
        servers = [server.decode() for server in servers]

        return servers




if __name__ == "__main__":
    # proxy_pool = ProxyPool(redis_host="192.168.153.128", redis_port=6379, redis_password="123456Jc", redis_db=15, pool_name="JcProxyPool")

    # proxy_pool.delete("114.104.134.198:8889")

    # proxy_pool.gt_score_threshold()

    # print(proxy_pool.count())
    # print(proxy_pool.query(use_times=5))

    ...
