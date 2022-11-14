from gevent import monkey;monkey.patch_all()
import gevent
import time
from faker import Faker
import random
import requests
from retrying import retry

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

fake = Faker()

# 查询ip服务
query_ip_urls = [
    "http://ifconfig.me",
    "https://www.cip.cc",
    "http://icanhazip.com/",
    "https://ident.me/",
    "https://ipecho.net/plain",
    "http://whatismyip.akamai.com/",
    "https://tnx.nl/ip",
    "https://myip.dnsomatic.com/",
    "https://ip.sb/"
]


class Schedule(object):

    def __init__(self):
        """
        初始化 redis，vps
        """

        self._proxy_pool = ProxyPool()

        self._vps_list = []
        for vps_data in vps_pool:
            try:
                vps_cli = VpsClient(**vps_data)
                # self.restart_tinyproxy(vps_cli)    # 重启tinyproxy
                self._vps_list.append(vps_cli)
            except Exception as e:
                logger.error(f"[vps]: {vps_data['server_name']} - {e}")


    def restart_tinyproxy(self, vps: VpsClient):
        """
        重启 tinyproxy
        :param vps:
        :return:
        """

        with gevent.Timeout(10, False) as timeout:

            vps.open_ssh()

            cmd = "systemctl restart tinyproxy"
            vps._exec_cmd(cmd)

            vps.close_ssh()


    def check_ip(self, server):
        """
        检测代理是否可用；
        :param server:
        :return:
        """

        try:
            headers = {
                "user_agent": fake.user_agent()
            }

            proxies = {
                "http": f"http://{server}",
                "https": f"http://{server}",
            }

            resp = requests.get(random.choice(query_ip_urls), headers=headers, proxies=proxies, timeout=20)
            if resp.status_code == 200:
                return True
        except Exception as e:
            pass

        return False


    @retry(stop_max_attempt_number=3)
    def dial(self, vps: VpsClient) -> str:
        """
        单次拨号, 并保存
        :param vps:
        :return:
        """
        server = ""

        # 超时断开,防止阻塞
        with gevent.Timeout(20, False) as timeout:
            vps.open_ssh()

            old_server = vps.current_server
            # 清除旧代理
            if self._proxy_pool.isExist(old_server):
                self._proxy_pool.delete(old_server)

            vps.adsl_stop()
            vps.adsl_start()
            server = vps.get_ip()

            vps.close_ssh()

        if server:
            # 防止tinyproxy失效
            if self.check_ip(server):

                self._proxy_pool.add([server])
                logger.success(f"[vps]: [{vps.vps_name}] replace proxy {server}")

            else:
                self.restart_tinyproxy(vps)
                logger.warning(f"[vps]: {vps.vps_name} server[{server}] can`t use")
                raise Exception(f"[vps]: {vps.vps_name} server[{server}] can`t use")
        else:
            logger.warning(f"[vps]: {vps.vps_name} server get is empty")

        return server

    def run_interval_dial(self):
        """
        间隔拨号
        :return:
        """

        # 清空池
        self._proxy_pool.delete(all=True)

        while True:

            mid_len = len(self._vps_list) // 2

            # 协程拨号
            jobs = []
            for vps in self._vps_list[:mid_len]:
                job = gevent.spawn(self.dial, vps)

                jobs.append(job)

            gevent.joinall(jobs)

            # print("----")

            jobs = []
            for vps in self._vps_list[mid_len:]:
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
