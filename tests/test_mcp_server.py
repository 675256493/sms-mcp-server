#!/usr/bin/env python3
"""
MCP Server 单元测试
"""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer, detect_carrier, batch_detect_carriers


class TestMCPServer(unittest.TestCase):
    """MCP Server 测试类"""

    def setUp(self):
        """测试前准备"""
        self.server = MCPServer()

    def test_get_capabilities(self):
        """测试获取服务器能力"""
        response = self.server.get_capabilities()

        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("result", response)
        self.assertEqual(response["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(
            response["result"]["serverInfo"]["name"], "phone-carrier-detector"
        )
        self.assertEqual(response["result"]["serverInfo"]["version"], "1.0.0")

    def test_list_tools(self):
        """测试工具列表"""
        response = self.server.list_tools()

        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("result", response)
        tools = response["result"]["tools"]

        # 检查工具数量
        self.assertEqual(len(tools), 2)

        # 检查工具名称
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("detect_carrier", tool_names)
        self.assertIn("batch_detect_carriers", tool_names)

        # 检查工具描述
        for tool in tools:
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)

    def test_call_tool_missing_parameter(self):
        """测试缺少参数的工具调用"""
        response = self.server.call_tool("detect_carrier", {})

        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Missing required parameter", response["error"]["message"])

    def test_call_tool_unknown_tool(self):
        """测试未知工具调用"""
        response = self.server.call_tool("unknown_tool", {})

        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)
        self.assertIn("Method not found", response["error"]["message"])


class TestPhoneDetection(unittest.TestCase):
    """手机号检测功能测试"""

    def test_detect_carrier_invalid_format(self):
        """测试无效格式的手机号"""
        # 测试非11位数字
        result = detect_carrier("123")
        self.assertFalse(result["success"])
        self.assertIn("Invalid phone number format", result["error"])

        # 测试不以1开头的号码
        result = detect_carrier("23456789012")
        self.assertFalse(result["success"])
        self.assertIn("Invalid phone number format", result["error"])

        # 测试包含非数字字符
        result = detect_carrier("138-1234-5678")
        self.assertFalse(result["success"])
        self.assertIn("Invalid phone number format", result["error"])

    def test_detect_carrier_valid_format(self):
        """测试有效格式的手机号"""
        # 这些测试需要数据库中有对应的记录
        # 如果数据库中没有这些前缀，会返回 not found 错误
        result = detect_carrier("13812345678")

        # 检查返回格式
        self.assertIn("success", result)
        self.assertIn("phone_number", result)
        self.assertIn("prefix", result)

        if result["success"]:
            self.assertIn("carrier", result)
            self.assertIn("carrier_cn", result)
            self.assertIn("province", result)
            self.assertIn("city", result)
            self.assertEqual(result["phone_number"], "13812345678")
            self.assertEqual(result["prefix"], "1381234")

    def test_batch_detect_carriers_invalid_input(self):
        """测试批量检测无效输入"""
        # 测试非列表输入
        result = batch_detect_carriers("not a list")
        self.assertFalse(result["success"])
        self.assertIn("Input must be a list", result["error"])

        # 测试超过100个号码
        large_list = [str(i) for i in range(101)]
        result = batch_detect_carriers(large_list)
        self.assertFalse(result["success"])
        self.assertIn("Maximum 100 phone numbers", result["error"])

    def test_batch_detect_carriers_valid_input(self):
        """测试批量检测有效输入"""
        phone_numbers = ["13812345678", "18687654321", "13312345678"]
        result = batch_detect_carriers(phone_numbers)

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(result["results"]), 3)

        # 检查每个结果
        for i, phone_result in enumerate(result["results"]):
            self.assertIn("success", phone_result)
            if phone_result["success"]:
                self.assertEqual(phone_result["phone_number"], phone_numbers[i])


class TestRequestHandling(unittest.TestCase):
    """请求处理测试"""

    def setUp(self):
        self.server = MCPServer()

    def test_handle_initialize_request(self):
        """测试初始化请求处理"""
        request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        self.server.request_id = request["id"]
        response = self.server.get_capabilities()
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)

    def test_handle_tools_list_request(self):
        """测试工具列表请求处理"""
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        self.server.request_id = request["id"]
        response = self.server.list_tools()
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 2)
        self.assertIn("result", response)

    def test_handle_tools_call_request(self):
        """测试工具调用请求处理"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "detect_carrier",
                "arguments": {"phone_number": "13812345678"},
            },
        }
        response = asyncio.run(self.server.handle_request(request))
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 3)
        self.assertIn("result", response)

    def test_handle_unknown_method(self):
        """测试未知方法处理"""
        request = {"jsonrpc": "2.0", "id": 4, "method": "unknown_method", "params": {}}
        response = asyncio.run(self.server.handle_request(request))
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 4)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
