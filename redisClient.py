import redis
from typing import Optional, List

from settings import *


"""
1. 池用redis的有序集合维护
2. 代理操作：
    1. 入库
    2. 查询
    3. 删除
    4. 随机代理（平均分配）
    
"""



class ProxyPool(object):

    def __init__(self, redis_host: str = REDIS_HOST,
                 redis_port: int = REDIS_PORT,
                 redis_password: str = REDIS_PASSWORD,
                 redis_db: int = REDIS_DB,
                 pool_name: str = "PROXY_POOL"):

        """
        初始化

        :param redis_host:
        :param redis_port:
        :param redis_password:
        :param redis_db:
        """

        self._redis = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)

        self.pool_name = pool_name

    def add_proxy(self, server: str):

        """
        添加代理
        :param server: [ip]:[port]
        :return:
        """
        if not server:
            logger.warning(f"missing argument.")
        else:
            code = self._redis.zadd(self.pool_name, {server: 0})
            if code == 1:
                logger.info(f"add proxy: {server} in {self.pool_name}")
            else:
                logger.warning(f"add proxy: {server} fail.")


    def query_proxy(self, size: int = -1) -> List[str]:
        """
        查询代理，返回代理列表
        :param size: 返回个数；-1：代表返回所有
        :return:
        """

        proxy_list = self._redis.zrange(self.pool_name, 0, size)
        proxy_list = [proxy.decode() for proxy in proxy_list]

        return proxy_list

    def del_proxy(self, server: str):
        """
        删除指定代理
        :param server: [ip]:[port]
        :return:
        """

        if not server:
            logger.warning(f"missing argument.")
        else:
            code = self._redis.zrem(self.pool_name, server)
            if code == 1:
                logger.info(f"del proxy: {server} in {self.pool_name}")
            else:
                logger.warning(f"del proxy: {server} fail.")

    def random_proxy(self, size):
        ...


if __name__ == "__main__":

    proxy_pool = ProxyPool()

    # proxy_pool.add_proxy("1.1.1.1:321")

    # proxy_list = proxy_pool.query_proxy()
    # print(proxy_list)

    # proxy_pool.del_proxy("1.1.1.1:321")
    ...




