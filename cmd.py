import click

from settings import *
from server import runserver

"""
版本查看
web服务启动
开启拨号
"""


@click.command(context_settings=dict(help_option_names=['-h', '--help']), no_args_is_help=True)
@click.option("-v", "--version", help="查看版本", is_flag=True)
@click.option("-s", "--server", help="启动接口", is_flag=True)
@click.option("-d", "--dial", help="开始拨号; 1: 定时拨号；2：阈值拨号", default="1", type=click.Choice(["1", "2"]))
def main(**kwargs):

    if kwargs.get("version"):
        print(VERSION)
    elif kwargs.get("server"):
        # 启动接口
        runserver()

    elif dial := kwargs.get("dial"):
        # 开启拨号

        from schedule import Schedule

        sche = Schedule()

        if dial == "1":
            sche.run_interval_dial()
        elif dial == "2":
            sche.run_time_dial()


if __name__ == '__main__':
    main()


    ...
