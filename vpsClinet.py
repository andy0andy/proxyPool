import random
import paramiko
from typing import Optional
import re
import time

from settings import *

"""
vps相关管理
1. 自动拨号
2. 拨号控频
3. 获取代理
"""


class VpsClient(object):
    ssh = None

    def __init__(self, **kwargs):

        self.vps_host = kwargs.get("host")
        self.vps_port = kwargs.get("port")
        self.vps_user = kwargs.get("user")
        self.vps_pass = kwargs.get("password")
        self.vps_out_port = kwargs.get("out_port")
        self.vps_name = kwargs.get("server_name")
        self.auth_user = kwargs.get("auth_user")
        self.auth_pass = kwargs.get("auth_pass")

        # 每次调用 get_ip方法，则记录当前ip
        self.current_server = ""
        self.open_ssh()
        self.get_ip()
        self.close_ssh()

    def open_ssh(self):
        """
        建立ssh连接vps
        :return:
        """

        # 建立连接
        trans = paramiko.Transport((self.vps_host, self.vps_port))
        trans.connect(username=self.vps_user, password=self.vps_pass)

        self.ssh = paramiko.SSHClient()
        self.ssh._transport = trans

        # 允许连接不在know_hosts文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def close_ssh(self):
        """
        关闭ssh连接
        :return:
        """

        self.ssh.close()

    def _exec_cmd(self, cmd: Optional[str] = ""):
        """
        执行命令
        :param cmd:
        :return:
        """

        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd, timeout=20)

        out_str = ssh_stdout.read().decode()
        err_str = ssh_stderr.read().decode()

        if out_str:
            return out_str
        else:
            return err_str

    def adsl_start(self, s: Optional[str] = dial_start):
        """
        开始拨号
        :param s:
        :return:
        """

        logger.info(f"[vps]: {self.vps_name} 开始拨号")
        self._exec_cmd(s)

    def adsl_stop(self, s: Optional[str] = dial_stop):
        """
        停止拨号
        :param s:
        :return:
        """

        logger.info(f"[vps]: {self.vps_name} 停止拨号")
        self._exec_cmd(s)

    def get_ip(self):
        """
        获取拨号后ip
        :return:
        """

        retval = self._exec_cmd("ip addr")

        comp = re.compile("inet ([\.\d]+?) peer")
        ip = "".join(comp.findall(retval))

        if ip:

            if self.auth_user and self.auth_pass:
                server = f"{self.auth_user}:{self.auth_pass}@{ip}:{self.vps_out_port}"
            else:
                server = f"{ip}:{self.vps_out_port}"

            self.current_server = server

            return server


