# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250529-104303
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
启动MCPServer，调用其中函数
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrettyPrintStr, PrintInline
import os

from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# from FuncForSettings import GetCurrentWorkParam
from InvokeMcpServer.LoadMcpServerConfig import LoadMcpServerConfig
from sqids import Sqids


class InvokeMcpServer:
    # SEP_MODU_FUNC = '.'  # 模块服务.工具函数名 分隔符
    SEP_MODU_FUNC = '#'  # 模块服务.工具函数名 分隔符

    def __init__(self, sWorkDir):
        # sWorkDir 工作目录，从 mcp.server 子目录下取得MCP配置
        self.sWorkDir = sWorkDir
        PrintTimeMsg(f'InvokeMcpServer.sWorkDir={self.sWorkDir}=')

        self.exit_stack = AsyncExitStack()

        oLoadConfig = LoadMcpServerConfig(self.sWorkDir)
        # self.dictCmdPath = GetCurrentWorkParam('dictCmdPath')
        # self.dictMcpServers = GetCurrentWorkParam('dictMcpServers')
        self.dictCmdPath = oLoadConfig.dictCmdPath
        self.dictMcpServers = oLoadConfig.dictMcpServers

        self.dictSessionByModuName = {}  # 通过 模块服务名 映射 Sessioon
        self.dictToolInfoByModuFuncName = {}  # 通过 模块服务.工具函数名 映射工具函数信息
        self.lsServFuncTools = []  # 为LLM准备的 MCP Server 服务端工具列表
        self.lsToolFunc4Print = []  # 工具函数简单描述信息列表，用于打印
        self.dictFuncNameByIdx = {}  # 通过模块函数顺序，找到模块函数字典 mf, 用于反向查找
        self.dictSchemaBySqids = {}  # 通过 Sqids 函数名，找到函数原型，用于LLM

        self.sqids = Sqids(
            alphabet='w5U4shrOSJvXbQq9MdtRTcI1oPKjlL8AkYCaVZHNye0G7zu6p3gWBxiEmfD2Fn',
            # alphabet='abcdefghijklmnopqrstuvwxyz',  # 仅小写字母
            min_length=5  # 最少字符数
        )

        self.iConnectMcpCount = 0

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def _register_one_mcp_server(self, sModuName, dictMcpServer):
        """注册一个MCP服务"""
        # sModuName 是MCP服务名，模块名
        sType = dictMcpServer.get('type', '')
        if sType not in ['stdio', 'sse']:
            PrintTimeMsg('_register_one_mcp_server({sModuName}).type={sType}=Error,SKIP!')
            return None
        if sType == 'stdio':
            sCmd = dictMcpServer.get('cmd', '')
            if not sCmd:
                sCmd = dictMcpServer.get('command', '')
            server_params = StdioServerParameters(
                command=self.dictCmdPath.get(sCmd, sCmd),
                args=dictMcpServer.get('args', []),
                env=dictMcpServer.get('env', None),
            )
            if self.iConnectMcpCount < 1:
                PrintTimeMsg(f'_register_one_mcp_server({sModuName}).server_params={server_params}=')
            rwContext = await self.exit_stack.enter_async_context(stdio_client(server_params))
            # read_stream, write_stream = rwContext
            # oSession = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            # await oSession.initialize()
            # PrintTimeMsg(f'_register_one_mcp_server({sModuName}).oSession.initialize!')
            # self.dictSessionByModuName[sModuName] = oSession
            # async with stdio_client(server_params) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByModuName[sModuName] = oSession
        else:
            sUrl = dictMcpServer.get('url', '')
            dictHeader = dictMcpServer.get('headers', {})
            if self.iConnectMcpCount < 1:
                PrintTimeMsg(f'_register_one_mcp_server({sModuName}).sUrl={sUrl},dictHeader={dictHeader}=')
            # 如下写法，oSession 被释放了
            # async with sse_client(sUrl, dictHeader) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByModuName[sModuName] = oSession
            rwContext = await self.exit_stack.enter_async_context(sse_client(sUrl, dictHeader))
        read_stream, write_stream = rwContext
        oSession = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return oSession

    async def connect_mcp_servers(self):
        """连接到多个MCP服务端"""
        for sModuName, dictMcpServer in self.dictMcpServers.items():
            # if sName.startswith('@'):  # 跳过代码示例
            #     continue
            # PrintTimeMsg(f'connect_mcp_servers({sModuName})={PrettyPrintStr(dictMcpServer)}=')
            oSession = await self._register_one_mcp_server(sModuName, dictMcpServer)
            if oSession:
                await oSession.initialize()
                if self.iConnectMcpCount < 1:
                    PrintTimeMsg(f'connect_mcp_servers({sModuName}).oSession.initialize!')
                self.dictSessionByModuName[sModuName] = oSession

        # PrintTimeMsg(f'connect_mcp_servers.dictSessionByModuName={self.dictSessionByModuName}=')
        if self.iConnectMcpCount < 1:
            PrintTimeMsg(f"connect_mcp_servers.len(self.dictSessionByModuName)={len(self.dictSessionByModuName)}=")
        await self._gather_available_tools()
        # await self._list_prompts()
        # PrintTimeMsg(f'connect_mcp_servers.lsServFuncTools={self.lsServFuncTools}=')
        self.iConnectMcpCount += 1
        return

    # async def _list_prompts(self):
    #     # 获取所有 Prompt 模板, WeiYF.测试内容为空
    #     lsPrompts = []
    #     for sModuName, oSession in self.dictSessionByModuName.items():
    #         response = await oSession.list_prompts()
    #         PrintTimeMsg(f'_list_prompts({sModuName})={PrettyPrintStr(response)}=')
    #         lsPrompts.append([prompt.name for prompt in response.prompts])
    #     PrintTimeMsg(f'_list_prompts()={PrettyPrintStr(lsPrompts)}=')

    def concatModuFuncName(self, sModuName, sFuncName):
        # 串接 模块服务.工具函数名 sModuFuncName = <sModuName>.<sFuncName>
        # 其中 sModuName 内部可能存在点 .
        return f'{sModuName}{self.SEP_MODU_FUNC}{sFuncName}'

    def parseModuFuncName(self, sModuFuncName):
        # 拆分 模块服务.工具函数名 为sModuName, sFuncName
        # 其中 sModuName 内部可能存在点 .
        sModuName, cSep, sFuncName = sModuFuncName.partition(self.SEP_MODU_FUNC)
        # lsV = sModuFuncName.split('.')
        # if len(lsV) > 0:
        #     sModuName = '.'.join(lsV[:-1])
        #     sFuncName = lsV[-1]
        # else:
        #     sModuName = ''
        #     sFuncName = ''
        return sModuName, sFuncName

    def parseSqidsFuncName(self, sSqidsFuncName):
        # 从 sSqidsFuncName 解析出 sModuName, sFuncName
        iModuleCnt, iFuncCnt = self.sqids.decode(sSqidsFuncName[1:])  # 去掉f前缀
        sIdx = '%s,%s' % (iModuleCnt, iFuncCnt)
        dictMF = self.dictFuncNameByIdx.get(sIdx, {})
        sModuName = dictMF.get('m', '')
        sFuncName = dictMF.get('f', '')
        return sModuName, sFuncName

    async def _gather_available_tools(self):
        """汇总所有MCP服务的工具列表"""
        self.lsServFuncTools = []
        self.dictToolInfoByModuFuncName = {}
        self.lsToolFunc4Print = []  # 工具函数简单描述信息列表，用于打印
        iModuleCnt = 0
        for sModuName, oSession in self.dictSessionByModuName.items():
            response = await oSession.list_tools()
            dictMcpServer = self.dictMcpServers[sModuName]
            disable_tools = dictMcpServer.get('disable_tools', [])
            iModuleCnt += 1
            iFuncCnt = 0
            for tool in response.tools:
                iFuncCnt += 1
                if tool.name in disable_tools:
                    continue
                sSqidsFuncName = 'f%s' % self.sqids.encode([iModuleCnt, iFuncCnt])
                # sModuSeq = f'm%.2d' % iModuleCnt
                # sFuncSeq = 'f%.3d' % iFuncCnt
                # sSqidsFuncName = f"{sModuSeq}{self.SEP_CHAR_NAME}{sFuncSeq}"
                sIdx = '%s,%s' % (iModuleCnt, iFuncCnt)
                self.dictFuncNameByIdx[sIdx] = {
                    'm': sModuName,
                    'f': tool.name,
                }
                dictToolInfo = {
                    "name": sSqidsFuncName,
                    "strict": True,  # 开启严格校验
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                    # 'required': tool.required,  # no required
                }
                self.lsServFuncTools.append({
                    "type": "function",  # OpenAI兼容写法
                    "function": dictToolInfo,
                })
                sModuFuncName = self.concatModuFuncName(sModuName, tool.name)
                self.dictToolInfoByModuFuncName[sModuFuncName] = dictToolInfo
                self.dictSchemaBySqids[sSqidsFuncName] = tool.inputSchema
                # if tool.name == 'get-juejin-article-rank':
                #     PrintTimeMsg(f"_gather_available_tools.tool.inputSchema={PrettyPrintStr(tool.inputSchema)}=")
                self.lsToolFunc4Print.append((sSqidsFuncName, sModuName, tool.name, tool.description))
                # lsFuncDetail.append((sSqidsFuncName, tool.name, tool.description, tool.inputSchema))

        # PrintTimeMsg(f"_gather_available_tools.lsServFuncTools={PrettyPrintStr(self.lsServFuncTools)}=")

        if self.iConnectMcpCount < 1:
            self.show_mcp_func_list()

    def show_mcp_func_list(self):
        # 打印MCP工具函数列表
        PrintTimeMsg(f"show_mcp_func_list.len(self.lsToolFunc4Print)={len(self.lsToolFunc4Print)}=")
        iIdx = 0
        for (sSqidsFuncName, sModuName, sFuncName, sDesc) in self.lsToolFunc4Print:
            iIdx += 1
            sHint = f'{iIdx}. {sSqidsFuncName}[{sModuName}{self.SEP_MODU_FUNC}{sFuncName}]'
            PrintInline(f"{sHint}={sDesc[:28]}\n")

    def show_mcp_func_info(self, sModuName=None, sFuncName=None, sModuFuncName=None, sSqidsFuncName=None):
        # 打印并返回MCP服务信息
        # 如果 sModuFuncName 或 sSqidsFuncName 被赋值，可以解析出 sModuName 和 sFuncName
        # 或者 sModuName 和 sFuncName 直接被赋值，
        # 则返回对应工具函数的描述和原型信息
        # 否则返回全部工具列表
        # PrintTimeMsg(f"show_mcp_func_info(sModuName={sModuName}, sFuncName={sFuncName}, sModuFuncName={sModuFuncName}, sSqidsFuncName={sSqidsFuncName})=...")
        if sModuFuncName:
            sModuName, sFuncName = self.parseModuFuncName(sModuFuncName)
        elif sSqidsFuncName:
            sModuName, sFuncName = self.parseSqidsFuncName(sSqidsFuncName)
        if sModuName and sFuncName:
            sMFName = self.concatModuFuncName(sModuName, sFuncName)
            dictToolInfo = self.dictToolInfoByModuFuncName.get(sMFName, {})
            PrintTimeMsg(f"show_mcp_func_info({sModuName}, {sFuncName})={PrettyPrintStr(dictToolInfo)}=")
        else:
            self.show_mcp_func_list()

    # async def _callbackTool(self, sFullFuncName, lsArgs):
    #     # 回调执行工具函数
    #     try:
    #         # PrintTimeMsg(f"_callbackTool(sName={sFullFuncName}, lsArgs={lsArgs})")
    #         # sModuSeq, cSep, sFuncSeq = sFullFuncName.partition(self.SEP_CHAR_NAME)  # .
    #         iModuleCnt, iFuncCnt = self.sqids.decode(sFullFuncName[1:])
    #         # iModuleCnt = int(sModuSeq[1:])
    #         # iFuncCnt = int(sFuncSeq[1:])
    #         sIdx = '%s,%s' % (iModuleCnt, iFuncCnt)
    #         dictMF = self.dictFuncNameByIdx.get(sIdx, {})
    #         sModuName = dictMF.get('m', '')
    #         sFuncName = dictMF.get('f', '')
    #         PrintTimeMsg(f"_callbackTool({sFullFuncName}={sModuName}.{sFuncName}({lsArgs})...")

    #         oSession = self.dictSessionByModuName.get(sModuName, None)
    #         if oSession:
    #             oResult = await oSession.call_tool(sFuncName, lsArgs)
    #             return oResult
    #     except Exception as e:
    #         PrintTimeMsg(f"_callbackTool({sFullFuncName}).e={repr(e)}")
    #         raise e
    #     raise Exception(f'_callbackTool.sFullFuncName={sFullFuncName}=NotFound!')

    # async def _callbackToolOrigin(self, sModuName, sFuncName, lsArgs):
    #     # 回调执行工具函数
    #     try:
    #         PrintTimeMsg(f"_callbackToolOrigin(sModuName={sModuName}, sFuncName={sFuncName}, lsArgs={lsArgs})")
    #         oSession = self.dictSessionByModuName.get(sModuName, None)
    #         if oSession:
    #             oResult = await oSession.call_tool(sFuncName, lsArgs)
    #             return oResult
    #     except Exception as e:
    #         PrintTimeMsg(f"_callbackTool(sModuName={sModuName}, sFuncName={sFuncName}).e={repr(e)}")
    #         raise e
    #     raise Exception(f'_callbackTool.sModuName={sModuName}, sFuncName={sFuncName}=NotFound!')

    # async def call_mcp_funcOrigin(self, sModuName, sFuncName, tool_args, callbackTool):
    #     # 通过模块名、函数名、参数，回调MCP工具函数
    #     self.lsMcpTextOut = []  # McpServer返回结果
    #     self.iToolCallCount = 0
    #     oResult = await callbackTool(sModuName, sFuncName, tool_args)
    #     for oContent in oResult.content:
    #         sMdText = oContent.text
    #         self.lsMcpTextOut.append(sMdText)
    #     return self

    def concat_mcp_out_text(self, oResult):
        # 串接mcp返回结果
        lsMcpTextOut = []  # McpServer返回结果
        if oResult and hasattr(oResult, 'content'):
            for oContent in oResult.content:
                sMdText = oContent.text
                lsMcpTextOut.append(sMdText)
        sResultMcpTextOut = '\n'.join(lsMcpTextOut)
        return sResultMcpTextOut

    async def call_mcp_func_origin(self, sModuName, sFuncName, dictArgs):
        # 通过模块名、函数名、参数，回调MCP工具函数
        self.iToolCallCount = 0
        try:
            sParamHint = f"{sModuName}, {sFuncName}, {dictArgs}"
            PrintTimeMsg(f"call_mcp_func_origin.sParamHint=({sParamHint})")
            oSession = self.dictSessionByModuName.get(sModuName, None)
            if oSession:
                oResult = await oSession.call_tool(sFuncName, dictArgs)
                return oResult
        except Exception as e:
            PrintTimeMsg(f"call_mcp_func_origin({sParamHint}).e={repr(e)}")
            raise e
        raise Exception(f'call_mcp_func_origin({sParamHint})=NotFound!')

    async def call_mcp_modu_func(self, sModuFuncName, dictArgs):
        sModuName, sFuncName = self.parseModuFuncName(sModuFuncName)
        return await self.call_mcp_func_origin(sModuName, sFuncName, dictArgs)

    async def call_mcp_func_sqids(self, sSqidsFuncName, dictArgs):
        # 回调执行工具函数
        try:
            sModuName, sFuncName = self.parseSqidsFuncName(sSqidsFuncName)
            return await self.call_mcp_func_origin(sModuName, sFuncName, dictArgs)
        except Exception as e:
            PrintTimeMsg(f"call_mcp_func_sqids({sSqidsFuncName}).e={repr(e)}")
            raise e

    async def loop_mcp_chat(self):
        """MCP交互聊天循环"""
        PrintTimeMsg("loop_mcp_chat.MCP Client Started!")
        # sHint = ','.join([f'{k}={v}' for k, v in self.dictFuncNameBySqids.items()])
        sHint = "Type your queries or 'quit' to exit."
        while True:
            try:
                sQuery = input(f"\n{sHint}\nQuery: ").strip()
                if not sQuery: continue
                if sQuery.lower() == 'quit':
                    break
                if sQuery.startswith('show'):
                    # 交互显示MCP工具函数列表
                    sParam = sQuery[4:].strip()
                    if sParam.startswith('f'):
                        self.show_mcp_func_info(sSqidsFuncName=sParam)
                    elif self.SEP_MODU_FUNC in sParam:
                        self.show_mcp_func_info(sModuFuncName=sParam)
                    else:
                        self.show_mcp_func_info()
                    continue
                dictArgs = {}
                if sQuery.startswith('#f'):
                    sSqidsFuncName = sQuery[1:]
                    oResult = await self.call_mcp_func_sqids(sSqidsFuncName, dictArgs)
                elif self.SEP_MODU_FUNC in sQuery:
                    sModuFuncName = sQuery
                    oResult = await self.call_mcp_modu_func(sModuFuncName, dictArgs)
                else:
                    sModuName, cSep, sFuncName = sQuery.partition(' ')
                    oResult = await self.call_mcp_func_origin(sModuName, sFuncName, dictArgs)
                mcp_text = self.concat_mcp_out_text(oResult)
                PrintTimeMsg(f"loop_mcp_chat.mcp_text={mcp_text}=")
            except Exception as e:
                PrintTimeMsg(f"loop_mcp_chat.e={repr(e)}=")

