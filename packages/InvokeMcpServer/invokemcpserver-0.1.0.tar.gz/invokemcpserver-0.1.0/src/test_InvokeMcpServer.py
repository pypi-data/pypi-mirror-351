# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250529-100152
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
Program description
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
import os
from InvokeMcpServer import InvokeMcpServer
import asyncio


async def mainInvokeMcpServer():
    sWorkDir = os.getcwd()
    client = InvokeMcpServer(sWorkDir)
    try:
        await client.connect_mcp_servers()
        await client.loop_mcp_chat()
    finally:
        await client.cleanup()


def asyncio_loop_run(cbASyncFunc):
    # 循环等待执行异步IO函数
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cbASyncFunc())


if __name__ == '__main__':
    PrintTimeMsg(f'__main__.sys.path={sys.path}')
    asyncio_loop_run(mainInvokeMcpServer)
