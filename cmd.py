import click
import uvicorn

from settings import *
from server import app

"""
版本查看
web服务启动
开启拨号
"""


@click.command(context_settings=dict(help_option_names=['-h', '--help']), no_args_is_help=True)
@click.option("-v", "--version", help="查看版本", is_flag=True)
@click.option("-s", "--server", help="启动接口", is_flag=True)
@click.option("-d", "--dial", help="开始拨号", is_flag=True)
def main(**kwargs):

    if kwargs.get("version"):
        print(VERSION)
    elif kwargs.get("server"):
        # 启动接口
        uvicorn.run("cmd:app", port=8081, reload=True, debug=True)

    elif kwargs.get("dial"):
        # 开启拨号
        ...



if __name__ == '__main__':
    main()
