#!/usr/bin/env python3
"""
MCP Server 集成测试
"""

import asyncio
import json
import subprocess
import sys
import os
import unittest
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MCPIntegrationTest(unittest.TestCase):
    """MCP Server 集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.server_process = None
        self.server_cmd = "python mcp_server.py"

    async def start_server(self):
        """启动 MCP server"""
        self.server_process = await asyncio.create_subprocess_exec(
            *self.server_cmd.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        print(f"🚀 启动 MCP server: {self.server_cmd}")

    async def send_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """发送请求到 MCP server"""
        if params is None:
            params = {}

        request = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}

        # 发送请求
        request_line = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_line.encode())
        await self.server_process.stdin.drain()

        # 读取响应
        response_line = await self.server_process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode().strip())
        else:
            return {"error": "No response"}

    async def stop_server(self):
        """停止 MCP server"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🛑 服务器已关闭")

    def test_server_initialization(self):
        """测试服务器初始化"""

        async def run_test():
            await self.start_server()

            # 发送初始化请求
            response = await self.send_request("initialize")

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("result", response)
            self.assertEqual(response["result"]["protocolVersion"], "2024-11-05")
            self.assertEqual(
                response["result"]["serverInfo"]["name"], "phone-carrier-detector"
            )
            self.assertEqual(response["result"]["serverInfo"]["version"], "1.0.0")

            await self.stop_server()

        asyncio.run(run_test())

    def test_tools_listing(self):
        """测试工具列表获取"""

        async def run_test():
            await self.start_server()

            # 发送工具列表请求
            response = await self.send_request("tools/list")

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("result", response)
            tools = response["result"]["tools"]

            # 检查工具数量
            self.assertEqual(len(tools), 2)

            # 检查工具名称
            tool_names = [tool["name"] for tool in tools]
            self.assertIn("detect_carrier", tool_names)
            self.assertIn("batch_detect_carriers", tool_names)

            await self.stop_server()

        asyncio.run(run_test())

    def test_single_phone_detection(self):
        """测试单个手机号检测"""

        async def run_test():
            await self.start_server()

            # 发送单个手机号检测请求
            response = await self.send_request(
                "tools/call",
                {
                    "name": "detect_carrier",
                    "arguments": {"phone_number": "13812345678"},
                },
            )

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("result", response)
            self.assertIn("content", response["result"])

            # 解析内容
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)

            # 检查返回格式
            self.assertIn("success", data)
            self.assertIn("phone_number", data)
            self.assertIn("prefix", data)

            if data["success"]:
                self.assertIn("carrier", data)
                self.assertIn("carrier_cn", data)
                self.assertIn("province", data)
                self.assertIn("city", data)
                self.assertEqual(data["phone_number"], "13812345678")
                self.assertEqual(data["prefix"], "1381234")

            await self.stop_server()

        asyncio.run(run_test())

    def test_batch_phone_detection(self):
        """测试批量手机号检测"""

        async def run_test():
            await self.start_server()

            # 发送批量检测请求
            response = await self.send_request(
                "tools/call",
                {
                    "name": "batch_detect_carriers",
                    "arguments": {
                        "phone_numbers": ["13812345678", "18687654321", "13312345678"]
                    },
                },
            )

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("result", response)
            self.assertIn("content", response["result"])

            # 解析内容
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)

            # 检查返回格式
            self.assertTrue(data["success"])
            self.assertEqual(data["total"], 3)
            self.assertEqual(len(data["results"]), 3)

            # 检查每个结果
            for i, phone_result in enumerate(data["results"]):
                self.assertIn("success", phone_result)
                if phone_result["success"]:
                    self.assertIn("phone_number", phone_result)
                    self.assertIn("carrier", phone_result)
                    self.assertIn("province", phone_result)
                    self.assertIn("city", phone_result)

            await self.stop_server()

        asyncio.run(run_test())

    def test_invalid_phone_number(self):
        """测试无效手机号处理"""

        async def run_test():
            await self.start_server()

            # 发送无效手机号检测请求
            response = await self.send_request(
                "tools/call",
                {"name": "detect_carrier", "arguments": {"phone_number": "123"}},
            )

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("result", response)

            # 解析内容
            content = response["result"]["content"][0]["text"]
            data = json.loads(content)

            # 检查错误信息
            self.assertFalse(data["success"])
            self.assertIn("error", data)
            self.assertIn("Invalid phone number format", data["error"])

            await self.stop_server()

        asyncio.run(run_test())

    def test_missing_parameter(self):
        """测试缺少参数处理"""

        async def run_test():
            await self.start_server()

            # 发送缺少参数的请求
            response = await self.send_request(
                "tools/call", {"name": "detect_carrier", "arguments": {}}
            )

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("error", response)
            self.assertEqual(response["error"]["code"], -32602)
            self.assertIn("Missing required parameter", response["error"]["message"])

            await self.stop_server()

        asyncio.run(run_test())

    def test_unknown_method(self):
        """测试未知方法处理"""

        async def run_test():
            await self.start_server()

            # 发送未知方法请求
            response = await self.send_request("unknown_method", {})

            # 验证响应
            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertIn("error", response)
            self.assertEqual(response["error"]["code"], -32601)
            self.assertIn("Method not found", response["error"]["message"])

            await self.stop_server()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
