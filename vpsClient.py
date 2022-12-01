from pydantic import BaseModel
from typing import Optional, List, Union
import re
import time
import warnings
from cryptography.utils import CryptographyDeprecationWarning
from retrying import retry

from settings import *

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko
    from paramiko.transport import Transport
    from paramiko.channel import Channel

"""
vps相关管理
1. 自动拨号
2. 拨号控频
3. 获取代理
"""


class Vps(BaseModel, object):
    # ssh机器连接信息
    host: Optional[str] = None
    port: Optional[int] = 22
    user: Optional[str] = "root"
    password: Optional[str] = None

    name: Optional[str] = None  # 机器对外名称
    out_port: Optional[int] = None  # 代理对外端口
    auth_user: Optional[str] = None  # 代理用户名
    auth_pass: Optional[str] = None  # 代理密码

    current_ip: Optional[str] = None  # 当前ip
    current_server: Optional[str] = None  # 当前可用代理

    _trans: Optional[Transport] = None  #
    _channel: Optional[Channel] = None  #


class VpsClient(object):
    vps: Optional[Vps] = None
    _trans: Optional[Transport] = None  #
    _channel: Optional[Channel] = None  #

    def __init__(self, **data):

        self.vps = Vps(**data)

        # 启动一个终端
        self.open_terminal()
        # 获取当前ip，代理
        self.get_current_ip()


    @retry(stop_max_attempt_number=3)
    def open_terminal(self):
        # ssh启动一个终端连接

        self._trans = paramiko.Transport((self.vps.host, self.vps.port))  # 建立一个socket
        self._trans.start_client(timeout=10)  # 启动一个终端
        self._trans.auth_password(username=self.vps.user, password=self.vps.password)  # 登录

        self._channel = self._trans.open_session(timeout=10)  # 创建一个通道
        self._channel.get_pty()  # 获取终端
        self._channel.invoke_shell()  # 激活终端
        logger.info(f"[vps]: ({self.vps.name}) 终端启动")

        if not self._trans.is_alive() or (not self._channel or self._channel.closed):
            err_str = f"[vps]: ({self.vps.name}) 终端启动失败"
            logger.warning(err_str)
            raise Exception(err_str)

    def close_terminel(self):
        # 关闭终端

        if not self._channel.closed:
            self._channel.close()
            self._channel = None

        if self._trans.is_alive():
            self._trans.close()
            self._trans = None

        logger.info(f"[vps]: ({self.vps.name}) 终端关闭")

    @retry(stop_max_attempt_number=3)
    def exec_cmd(self, cmd: Optional[str] = "\n", separator: Union[str, List[str]] = "~]#", max_line: int = 66,
                 nbytes: int = 10240):
        """
        如果发生异常，则重连ssh

        :param cmd:  待执行命令，尽量避免类似 top等阻塞命令
        :param separator:  分隔符，入参可以是 字符串或列表，用以判断命令执行结束，结果也完全返回
        :param max_line: 单个命令返回结果最大接受次数，最后一次调用 ctrl+c 结束返回，避免类 top 命令
        :param nbytes: 单行最大接收字节
        :return:
        """

        if isinstance(separator, str):
            separator = [separator]

        cmd = cmd + "\n"

        try:

            # 发收消息
            self._channel.sendall(cmd.encode())  # 发
            time.sleep(0.5)

            # 收
            lines = []
            for i in range(max_line):  # 防止阻塞
                line = self._channel.recv(nbytes=nbytes).decode()
                lines.append(line)

                # 匹配结束符
                if any([line.replace("\n", "").replace("\r", "").strip().endswith(sep) for sep in separator]):
                    break

                if i == max_line - 1:
                    self._channel.sendall("\x03")  # ctrl + c

            rettxt = "".join(lines)
            return rettxt

        except OSError as os_e:

            err_str = f"[vps]: ({self.vps.name}) - {os_e}, 待异常重连"
            logger.error(err_str)

            # 重连
            self.close_terminel()
            self.open_terminal()

            raise Exception(err_str)

        except Exception as e:
            err_str = f"[vps]: ({self.vps.name}) - {e}"
            logger.exception(err_str)

    @retry(stop_max_attempt_number=3)
    def get_current_ip(self):

        cmd = "ip addr"
        rettxt = self.exec_cmd(cmd)

        comp = re.compile("inet ([\.\d]+?) peer")
        ip = "".join(comp.findall(rettxt))
        self.vps.current_ip = ip

        if ip:

            if self.vps.auth_user and self.vps.auth_pass:
                server = f"{self.vps.auth_user}:{self.vps.auth_pass}@{ip}:{self.vps.out_port}"
            else:
                server = f"{ip}:{self.vps.out_port}"

            self.vps.current_server = server

            return ip, server
        else:
            # ip获取不到，可能是上次拨号中断，重新拨号即可解决
            err_str = f"[vps]: ({self.vps.name}) - 获取IP，代理为空，拨号重试"
            logger.warning(err_str)

            self.adsl_stop()
            self.adsl_start()

            raise Exception(err_str)

    def adsl_start(self, cmd: Optional[str] = dial_start):
        """
        开始拨号
        :param cmd:
        :return:
        """

        if cmd:
            logger.info(f"[vps]: ({self.vps.name}) - 开始拨号")
            self.exec_cmd(cmd)

    def adsl_stop(self, cmd: Optional[str] = dial_stop):
        """
        停止拨号
        :param cmd:
        :return:
        """

        if cmd:
            logger.info(f"[vps]: ({self.vps.name}) - 停止拨号")
            self.exec_cmd(cmd)


if __name__ == '__main__':
    data = {
        "host": "114.104.147.16",
        "port": 20189,
        "user": "root",
        "password": "ZxHshan01",
        "name": "hshan01",
        "out_port": "6256",
        "auth_user": "zxkj",
        "auth_pass": "Wlhrag11",
    }

    vps_cli = VpsClient(**data)

    lines = vps_cli.exec_cmd(cmd="date")
    print(f"{lines}")

    vps_cli.close_terminel()
