#!/usr/bin/env python3
"""
标准的 MCP Server for Phone Carrier Detection
"""

import asyncio
import json
import re
import sys
from typing import Any, Dict


# 加载手机号数据库
def load_phone_database():
    """加载手机号数据库"""
    try:
        with open("data/phone_database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("警告: phone_database.json 文件不存在，使用默认数据库")
        return {}


# 手机号数据库
PHONE_DATABASE = load_phone_database()


def detect_carrier(phone_number: str) -> Dict[str, Any]:
    """检测手机号运营商和归属地"""
    # 验证手机号格式
    if not re.match(r"^1[3-9]\d{9}$", phone_number):
        return {
            "success": False,
            "error": "Invalid phone number format. Must be 11 digits starting with 1.",
        }

    # 提取前缀（前7位）
    prefix = phone_number[:7]

    # 查找数据库
    if prefix in PHONE_DATABASE:
        info = PHONE_DATABASE[prefix]
        return {
            "success": True,
            "phone_number": phone_number,
            "carrier": info["carrier"],
            "carrier_cn": info["carrier_cn"],
            "province": info["province"],
            "city": info["city"],
            "prefix": prefix,
        }
    else:
        return {
            "success": False,
            "error": f"Phone number prefix {prefix} not found in database",
        }


def batch_detect_carriers(phone_numbers: list) -> Dict[str, Any]:
    """批量检测手机号运营商和归属地"""
    if not isinstance(phone_numbers, list):
        return {"success": False, "error": "Input must be a list of phone numbers"}

    if len(phone_numbers) > 100:
        return {
            "success": False,
            "error": "Maximum 100 phone numbers allowed per batch",
        }

    results = []
    for phone in phone_numbers:
        if not isinstance(phone, str):
            results.append(
                {"success": False, "error": f"Invalid phone number type: {type(phone)}"}
            )
        else:
            results.append(detect_carrier(phone))

    return {"success": True, "results": results, "total": len(results)}


class MCPServer:
    """MCP Server 实现"""

    def __init__(self):
        self.request_id = 1

    def get_capabilities(self) -> Dict[str, Any]:
        """获取服务器能力"""
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "phone-carrier-detector", "version": "1.0.0"},
            },
        }

    def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "result": {
                "tools": [
                    {
                        "name": "detect_carrier",
                        "description": "Detect carrier and location for a single phone number",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "description": "Phone number to detect (11 digits)",
                                }
                            },
                            "required": ["phone_number"],
                        },
                    },
                    {
                        "name": "batch_detect_carriers",
                        "description": "Detect carriers and locations for multiple phone numbers",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "phone_numbers": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of phone numbers to detect (max 100)",
                                }
                            },
                            "required": ["phone_numbers"],
                        },
                    },
                ]
            },
        }

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        try:
            if name == "detect_carrier":
                phone_number = arguments.get("phone_number")
                if not phone_number:
                    return {
                        "jsonrpc": "2.0",
                        "id": self.request_id,
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: phone_number",
                        },
                    }
                result = detect_carrier(phone_number)
                return {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    result, ensure_ascii=False, indent=2
                                ),
                            }
                        ]
                    },
                }

            elif name == "batch_detect_carriers":
                phone_numbers = arguments.get("phone_numbers")
                if not phone_numbers:
                    return {
                        "jsonrpc": "2.0",
                        "id": self.request_id,
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: phone_numbers",
                        },
                    }
                result = batch_detect_carriers(phone_numbers)
                return {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    result, ensure_ascii=False, indent=2
                                ),
                            }
                        ]
                    },
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "error": {"code": -32601, "message": f"Method not found: {name}"},
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        self.request_id = request.get("id", 1)
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return self.get_capabilities()
        elif method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            return self.call_tool(name, arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }


async def main():
    """主函数"""
    server = MCPServer()

    # 使用标准输入输出
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    try:
        while True:
            # 读取一行
            line = await reader.readline()
            if not line:
                break

            try:
                # 解析 JSON
                request = json.loads(line.decode().strip())

                # 处理请求
                response = await server.handle_request(request)

                # 发送响应
                response_line = json.dumps(response) + "\n"
                sys.stdout.buffer.write(response_line.encode())
                sys.stdout.buffer.flush()

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
                error_line = json.dumps(error_response) + "\n"
                sys.stdout.buffer.write(error_line.encode())
                sys.stdout.buffer.flush()

            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                }
                error_line = json.dumps(error_response) + "\n"
                sys.stdout.buffer.write(error_line.encode())
                sys.stdout.buffer.flush()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
