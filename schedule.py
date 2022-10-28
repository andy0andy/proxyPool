from gevent import monkey;

monkey.patch_all()
import gevent
import time
from multiprocessing import Process
from queue import Queue

from settings import *
from vpsClinet import VpsClient
from proxyPool import ProxyPool

"""
拨号策略：
    定时拨号，间隔拨号
    协程拨号
代理使用策略：
    阈值：超过阈值拨号
"""


class Schedule(object):

    def __init__(self):
        """
        初始化 redis，vps
        """

        self._proxy_pool = ProxyPool()

        self._vps_list = []
        for vps_data in vps_pool:
            vps_cli = VpsClient(**vps_data)
            self._vps_list.append(vps_cli)

    def dial(self, vps: VpsClient) -> str:
        """
        单次拨号, 并保存
        :param vps:
        :return:
        """

        vps.open_ssh()

        old_server = vps.current_server
        vps.adsl_stop()
        vps.adsl_start()
        server = vps.get_ip()

        vps.close_ssh()

        # 清除旧代理
        if self._proxy_pool.isExist(old_server):
            self._proxy_pool.delete(old_server)

        self._proxy_pool.add([server])
        logger.success(f"[vps]: [{vps.vps_name}] replace proxy {server}")

        return server

    def run_interval_dial(self):
        """
        间隔拨号
        :return:
        """

        # 清空池
        self._proxy_pool.delete(all=True)

        while True:

            # 协程拨号
            jobs = []
            for vps in self._vps_list:
                job = gevent.spawn(self.dial, vps)

                jobs.append(job)

            gevent.joinall(jobs)

            time.sleep(dial_interval)

    def run_time_dial(self):
        """
        次数拨号，超过次数阈值则拨号换IP

        :return:
        """

        # 清空池
        self._proxy_pool.delete(all=True)

        while True:
            jobs = []

            if self._proxy_pool.count() == 0:
                logger.info(f"[dial]: gt score threshold [{dial_threshold}] - {len(self._vps_list)}")
                for vps in self._vps_list:
                    job = gevent.spawn(self.dial, vps)
                    jobs.append(job)

            else:
                servers = self._proxy_pool.gt_score_threshold()
                logger.info(f"[dial]: gt score threshold [{dial_threshold}] - {len(servers)}")
                for server in servers:
                    for vps in self._vps_list:
                        if vps.current_server == server:
                            job = gevent.spawn(self.dial, vps)
                            jobs.append(job)

            gevent.joinall(jobs)
            time.sleep(1)


if __name__ == '__main__':
    sche = Schedule()

    sche.run_interval_dial()
    # sche.run_time_dial()


    ...
