# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250428-104133
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
启动MCP客户端，连带MCP服务端
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrettyPrintStr, PrintAndSleep, PrintInline
import os
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

# from FuncForSettings import GetCurrentWorkParam
from LoadMcpServerConfig import LoadMcpServerConfig
from LlmServer import LlmServer
from FileQueryResult import FileQueryResult
from sqids import Sqids


class TaskMcpClient:
    # SEP_CHAR_NAME = '.'  # MCP Server 服务名与函数名的分隔符

    def __init__(self, sEnvFN='.env', sRunMode='task'):
        self.sRunMode = sRunMode
        self.sWorkDir = os.getcwd()
        PrintTimeMsg(f'TaskMcpClient.sWorkDir={self.sWorkDir}=')
        self.exit_stack = AsyncExitStack()

        oLoadConfig = LoadMcpServerConfig(self.sWorkDir)
        # self.dictCmdPath = GetCurrentWorkParam('dictCmdPath')
        # self.dictMcpServers = GetCurrentWorkParam('dictMcpServers')
        self.dictCmdPath = oLoadConfig.dictCmdPath
        self.dictMcpServers = oLoadConfig.dictMcpServers

        self.dictSessionByName = {}  # 通过 服务名 映射 Sessioon
        self.lsServFuncTools = []  # MCP Server 服务端工具列表
        self.oLlm = LlmServer(self.sWorkDir, sEnvFN)
        self.oFile = FileQueryResult(self.sWorkDir)

        self.sqids = Sqids(
            alphabet='w5U4shrOSJvXbQq9MdtRTcI1oPKjlL8AkYCaVZHNye0G7zu6p3gWBxiEmfD2Fn',
            # alphabet='abcdefghijklmnopqrstuvwxyz',  # 仅小写字母
            min_length=5  # 最少字符数
        )
        self.dictFuncNameBySqids = {}
        self.dictFuncNameByIdx = {}
        self.dictSchemaByFuncName = {}

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
            # self.dictSessionByName[sModuName] = oSession
            # async with stdio_client(server_params) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByName[sModuName] = oSession
        else:
            sUrl = dictMcpServer.get('url', '')
            dictHeader = dictMcpServer.get('headers', {})
            if self.iConnectMcpCount < 1:
                PrintTimeMsg(f'_register_one_mcp_server({sModuName}).sUrl={sUrl},dictHeader={dictHeader}=')
            # 如下写法，oSession 被释放了
            # async with sse_client(sUrl, dictHeader) as rwContext:
            #     async with ClientSession(*rwContext) as oSession:
            #         await oSession.initialize()
            #         self.dictSessionByName[sModuName] = oSession
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
                self.dictSessionByName[sModuName] = oSession

        # PrintTimeMsg(f'connect_mcp_servers.dictSessionByName={self.dictSessionByName}=')
        if self.iConnectMcpCount < 1:
            PrintTimeMsg(f"connect_mcp_servers.len(self.dictSessionByName)={len(self.dictSessionByName)}=")
        await self._gather_available_tools()
        # await self._list_prompts()
        # PrintTimeMsg(f'connect_mcp_servers.lsServFuncTools={self.lsServFuncTools}=')
        self.iConnectMcpCount += 1
        return

    # async def _list_prompts(self):
    #     # 获取所有 Prompt 模板, WeiYF.测试内容为空
    #     lsPrompts = []
    #     for sModuName, oSession in self.dictSessionByName.items():
    #         response = await oSession.list_prompts()
    #         PrintTimeMsg(f'_list_prompts({sModuName})={PrettyPrintStr(response)}=')
    #         lsPrompts.append([prompt.name for prompt in response.prompts])
    #     PrintTimeMsg(f'_list_prompts()={PrettyPrintStr(lsPrompts)}=')

    async def _gather_available_tools(self):
        """汇总所有MCP服务的工具列表"""
        self.lsServFuncTools = []
        lsFuncSimple = []  # Func简单描述信息列表，用于打印
        iModuleCnt = 0
        for sModuName, oSession in self.dictSessionByName.items():
            response = await oSession.list_tools()
            dictMcpServer = self.dictMcpServers[sModuName]
            disable_tools = dictMcpServer.get('disable_tools', [])
            iModuleCnt += 1
            iFuncCnt = 0
            for tool in response.tools:
                iFuncCnt += 1
                if tool.name in disable_tools:
                    continue
                sFullFuncName = 'f%s' % self.sqids.encode([iModuleCnt, iFuncCnt])
                # sModuSeq = f'm%.2d' % iModuleCnt
                # sFuncSeq = 'f%.3d' % iFuncCnt
                # sFullFuncName = f"{sModuSeq}{self.SEP_CHAR_NAME}{sFuncSeq}"
                sIdx = '%s,%s' % (iModuleCnt, iFuncCnt)
                self.dictFuncNameByIdx[sIdx] = {
                    'm': sModuName,
                    'f': tool.name,
                }
                self.dictFuncNameBySqids[sFullFuncName] = tool.name
                self.lsServFuncTools.append({
                    "type": "function",  # OpenAI兼容写法
                    "function": {
                        "name": sFullFuncName,
                        "strict": True,  # 开启严格校验
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                        # 'required': tool.required,  # no required
                    }
                })
                self.dictSchemaByFuncName[sFullFuncName] = tool.inputSchema
                # if tool.name == 'get-juejin-article-rank':
                #     PrintTimeMsg(f"_gather_available_tools.tool.inputSchema={PrettyPrintStr(tool.inputSchema)}=")
                lsFuncSimple.append((sFullFuncName, tool.name, tool.description))
                # lsFuncDetail.append((sFullFuncName, tool.name, tool.description, tool.inputSchema))

        # PrintTimeMsg(f"_gather_available_tools.lsServFuncTools={PrettyPrintStr(self.lsServFuncTools)}=")
        PrintTimeMsg(f"_gather_available_tools.len(lsFuncSimple)={len(lsFuncSimple)}=")
        if self.iConnectMcpCount < 1:
            iIdx = 0
            for (sFunc, sTool, sDesc) in lsFuncSimple:
                iIdx += 1
                if self.sRunMode == 'chat':
                    sSchema = self.dictSchemaByFuncName[sFunc]
                    PrintInline(f"{iIdx}. {sFunc}[{sTool}]={sDesc}={sSchema}\n")
                else:
                    PrintInline(f"{iIdx}. {sFunc}[{sTool}]={sDesc[:30]}\n")

    async def _callbackTool(self, sFullFuncName, lsArgs):
        # 回调执行工具函数
        try:
            # PrintTimeMsg(f"_callbackTool(sName={sFullFuncName}, lsArgs={lsArgs})")
            # sModuSeq, cSep, sFuncSeq = sFullFuncName.partition(self.SEP_CHAR_NAME)  # .
            iModuleCnt, iFuncCnt = self.sqids.decode(sFullFuncName[1:])
            # iModuleCnt = int(sModuSeq[1:])
            # iFuncCnt = int(sFuncSeq[1:])
            sIdx = '%s,%s' % (iModuleCnt, iFuncCnt)
            dictMF = self.dictFuncNameByIdx.get(sIdx, {})
            sModuName = dictMF.get('m', '')
            sFuncName = dictMF.get('f', '')
            PrintTimeMsg(f"_callbackTool({sFullFuncName}={sModuName}.{sFuncName}({lsArgs})...")

            oSession = self.dictSessionByName.get(sModuName, None)
            if oSession:
                oResult = await oSession.call_tool(sFuncName, lsArgs)
                return oResult
        except Exception as e:
            PrintTimeMsg(f"_callbackTool({sFullFuncName}).e={repr(e)}")
            raise e
        raise Exception(f'_callbackTool.sFullFuncName={sFullFuncName}=NotFound!')

    async def loop_mcp_chat(self):
        """MCP交互聊天循环"""
        PrintTimeMsg("loop_mcp_chat.MCP Client Started!")
        # PrintTimeMsg("Type your queries or 'quit' to exit.")
        sHint = ','.join([f'{k}={v}' for k,v in self.dictFuncNameBySqids.items()])
        while True:
            try:
                sQuery = input(f"\n{sHint}\nQuery: ").strip()
                if not sQuery: continue
                if sQuery.lower() == 'quit':
                    break
                # sQuery = '洛杉矶的天气怎样？'
                # # sQuery = '1234 + 7890 = ?'
                # sQuery = 'xuanyuan的视频里面，网络安全主题相关的播放最高的是哪个?'
                # 调用LLM及工具
                if sQuery.startswith('#f'):
                    tool_name = sQuery[1:]
                    tool_args = {}
                    await self.oLlm.call_mcp_func(tool_name, tool_args, self._callbackTool)
                    mcp_text = '\n'.join(self.oLlm.lsMcpTextOut)
                    PrintTimeMsg(f"loop_mcp_chat.mcp_text={mcp_text}=")
                else:
                    PrintTimeMsg(f"loop_mcp_chat.sQuery={sQuery}=")
                    await self.oLlm.process_query(sQuery, self.lsServFuncTools, self._callbackTool, self.dictSchemaByFuncName)
                    # mcp_text = '\n'.join(self.oLlm.lsMcpTextOut)
                    # PrintTimeMsg(f"loop_mcp_chat.mcp_text={mcp_text}=")
                    final_text = '\n'.join(self.oLlm.lsFinalTextOut)
                    PrintTimeMsg(f"loop_mcp_chat.final_text={final_text}=")
            except Exception as e:
                PrintTimeMsg(f"loop_mcp_chat.e={repr(e)}=")

    # async def loop_mcp_file_query(self):
    #     """MCP循环监听处理文件请求"""
    #     PrintTimeMsg("loop_mcp_file_query.MCP Client Started!")

    #     async def callbackQueryResult(sQueryText):
    #         PrintTimeMsg(f"callbackQueryResult.sQueryText={sQueryText}=")
    #         await self.oLlm.process_query(sQueryText, self.lsServFuncTools, self._callbackTool)
    #         return self.oLlm

    #     iLoopCnt = 0
    #     while True:
    #         iSleepSeconds = 60
    #         try:
    #             lsNoExtFN = self.oFile.list_file_query_task()
    #             for sNoExtFN in lsNoExtFN:
    #                 await self.oFile.deal_file_query_result(sNoExtFN, callbackQueryResult)
    #         except Exception as e:
    #             PrintTimeMsg(f"loop_mcp_file_query.e={repr(e)}=")
    #         PrintAndSleep(iSleepSeconds, f'loop_mcp_file_query.iLoopCnt={iLoopCnt}', iLoopCnt % 10 == 0)
    #         iLoopCnt += 1

async def loop_mcp_file_task(sEnvFN):
    # MCP循环监听处理文件请求
    # oTMC = oTaskMcpClient
    PrintTimeMsg("loop_mcp_file_task.MCP Client Started!")
    iLoopCnt = 0
    oTMC = TaskMcpClient(sEnvFN)
    async def callbackQueryResult(sQueryText):
        PrintTimeMsg(f"callbackQueryResult.sQueryText={sQueryText}=")
        await oTMC.oLlm.process_query(sQueryText, oTMC.lsServFuncTools, oTMC._callbackTool, oTMC.dictSchemaByFuncName)
        return oTMC.oLlm
    while True:
        iSleepSeconds = 60
        try:
            lsNoExtFN = oTMC.oFile.list_file_query_task()
            if lsNoExtFN:
                await oTMC.connect_mcp_servers()
                for sNoExtFN in lsNoExtFN:
                    await oTMC.oFile.deal_file_query_result(sNoExtFN, callbackQueryResult)
        except Exception as e:
            PrintTimeMsg(f"loop_mcp_file_task.e={repr(e)}=")
        finally:
            await oTMC.cleanup()
        PrintAndSleep(iSleepSeconds, f'loop_mcp_file_task.iLoopCnt={iLoopCnt}', iLoopCnt % 10 == 0)
        iLoopCnt += 1

async def mainTaskMcpClient():
    sRunMode = 'chat'  # 默认是聊天模式
    sEnvFN = '.env'  # 环境变量配置文件
    if len(sys.argv) >= 2:
        sRunMode = sys.argv[1]
        if len(sys.argv) >= 3:
            sEnvFN = sys.argv[2]

    if sRunMode == 'task':
        return await loop_mcp_file_task(sEnvFN)

    client = TaskMcpClient(sEnvFN, sRunMode)
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


def main():
    asyncio_loop_run(mainTaskMcpClient)


if __name__ == '__main__':
    main()
