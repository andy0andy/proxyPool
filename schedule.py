from gevent import monkey;

monkey.patch_all()
import gevent
import time
from faker import Faker
import random
import requests
from retrying import retry

from settings import *
from vpsClient import VpsClient
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
    "https://pinduoduo.com/",
    "https://www.taobao.com/",
    "https://www.sogou.com/",
    "https://www.so.com/",
    "http://www.bing.com",
    "http://www.baidu.com",
    "http://ifconfig.me",
    "http://icanhazip.com/",
    "https://ipecho.net/plain",
    "http://whatismyip.akamai.com/",
]


class Schedule(object):

    def __init__(self):
        """
        初始化 redis，vps
        """

        self._proxy_pool = ProxyPool()


        def add_vps_list(vps_data):
            try:
                vps_cli = VpsClient(**vps_data)

                self._vps_list.append(vps_cli)
            except Exception as e:
                logger.error(f"[vps]: ({vps_data['name']} - {e}")

        self._vps_list = []
        jobs = []
        for vps_data in vps_pool:
            job = gevent.spawn(add_vps_list, vps_data)
            jobs.append(job)

        gevent.joinall(jobs)

    def restart_reverse_tool(self, vps_cli: VpsClient):
        """
        重启 反向代理工具
        :param vps:
        :return:
        """

        with gevent.Timeout(10, False) as timeout:
            cmd = "systemctl restart squid"
            vps_cli.exec_cmd(cmd)

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

            url = random.choice(query_ip_urls)
            resp = requests.get(url=url, headers=headers, proxies=proxies, timeout=10)
            if resp.status_code == 200:
                return True
        except Exception as e:
            pass

        return False

    @retry(stop_max_attempt_number=3)
    def dial(self, vps_cli: VpsClient) -> str:
        """
        单次拨号, 并保存
        :param vps:
        :return:
        """
        server = ""

        # 超时断开,防止阻塞
        with gevent.Timeout(20, False) as timeout:

            old_server = vps_cli.vps.current_server
            # 清除旧代理
            if old_server and self._proxy_pool.isExist(old_server):
                self._proxy_pool.delete(old_server)

            # 拨号
            vps_cli.adsl_stop(dial_stop)
            vps_cli.adsl_start(dial_start)
            ip, server = vps_cli.get_current_ip()

        if server:
            # 防止反向代理工具失效
            if self.check_ip(server):

                self._proxy_pool.add([server])
                logger.success(f"[vps]: [{vps_cli.vps.name}] replace proxy {server}")

            else:
                self.restart_reverse_tool(vps_cli)

                err_str = f"[vps]: {vps_cli.vps.name} server[{server}] can`t use"
                logger.warning(err_str)
                raise Exception(err_str)
        else:
            err_str = f"[vps]: {vps_cli.vps.name} server get is empty"
            logger.warning(err_str)
            raise Exception(err_str)

        return server

    def run_interval_dial(self, batch=2):
        """
        间隔拨号
        :return:
        """

        # 清空池
        self._proxy_pool.delete(all=True)

        while True:

            # 分批拨号
            # 单次拨号量
            single_dial_vilume = len(self._vps_list) // batch

            for i in range(batch):
                if i == batch - 1:
                    pend_vps_list = self._vps_list[i * single_dial_vilume:]
                else:
                    pend_vps_list = self._vps_list[i * single_dial_vilume: (i + 1) * single_dial_vilume]

                # 协程拨号
                jobs = []
                for vps in pend_vps_list:
                    job = gevent.spawn(self.dial, vps)

                    jobs.append(job)

                gevent.joinall(jobs)

            # 拨号间隔
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
                for vps_cli in self._vps_list:
                    job = gevent.spawn(self.dial, vps_cli)
                    jobs.append(job)

            else:
                servers = self._proxy_pool.gt_score_threshold()
                logger.info(f"[dial]: gt score threshold [{dial_threshold}] - {len(servers)}")
                for server in servers:
                    for vps_cli in self._vps_list:
                        if vps_cli.vps.current_server == server:
                            job = gevent.spawn(self.dial, vps_cli)
                            jobs.append(job)

            gevent.joinall(jobs)
            time.sleep(1)


if __name__ == '__main__':
    sche = Schedule()

    # 测试偶然vps断开连接，重连阻塞时间过过长问题
    sche.run_interval_dial()


    ...
