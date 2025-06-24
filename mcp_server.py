#!/usr/bin/env python3
"""
MCP Server for Phone Carrier Detection
"""

import asyncio
import json
import logging
import re
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP server实例
server = Server("phone-carrier-detector")

# 运营商数据库
CARRIER_DATABASE = {
    # 中国移动
    "134": "China Mobile",
    "135": "China Mobile",
    "136": "China Mobile",
    "137": "China Mobile",
    "138": "China Mobile",
    "139": "China Mobile",
    "147": "China Mobile",
    "150": "China Mobile",
    "151": "China Mobile",
    "152": "China Mobile",
    "157": "China Mobile",
    "158": "China Mobile",
    "159": "China Mobile",
    "172": "China Mobile",
    "178": "China Mobile",
    "182": "China Mobile",
    "183": "China Mobile",
    "184": "China Mobile",
    "187": "China Mobile",
    "188": "China Mobile",
    "198": "China Mobile",
    # 中国联通
    "130": "China Unicom",
    "131": "China Unicom",
    "132": "China Unicom",
    "145": "China Unicom",
    "146": "China Unicom",
    "155": "China Unicom",
    "156": "China Unicom",
    "166": "China Unicom",
    "167": "China Unicom",
    "175": "China Unicom",
    "176": "China Unicom",
    "185": "China Unicom",
    "186": "China Unicom",
    # 中国电信
    "133": "China Telecom",
    "149": "China Telecom",
    "153": "China Telecom",
    "173": "China Telecom",
    "177": "China Telecom",
    "180": "China Telecom",
    "181": "China Telecom",
    "189": "China Telecom",
    "199": "China Telecom",
    # 虚拟运营商
    "170": "Virtual Carrier",
    "171": "Virtual Carrier",
    "174": "Virtual Carrier",
}


def detect_carrier(phone_number: str) -> Dict[str, Any]:
    """
    检测手机号码的运营商信息

    Args:
        phone_number: 手机号码

    Returns:
        包含运营商信息的字典
    """
    # 清理号码，只保留数字
    clean_number = re.sub(r"\D", "", phone_number)

    # 验证号码长度
    if len(clean_number) != 11:
        return {
            "phone_number": phone_number,
            "clean_number": clean_number,
            "carrier": "Unknown Carrier",
            "error": "Invalid phone number length",
            "message": "Phone number must be 11 digits",
            "is_valid": False,
        }

    # 验证号码格式
    if not clean_number.startswith("1"):
        return {
            "phone_number": phone_number,
            "clean_number": clean_number,
            "carrier": "Unknown Carrier",
            "error": "Invalid phone number format",
            "message": "Phone number must start with '1'",
            "is_valid": False,
        }

    # 获取前三位作为运营商前缀
    prefix = clean_number[:3]

    # 查找运营商
    carrier = CARRIER_DATABASE.get(prefix, "Unknown Carrier")

    # 确定号码类型
    if prefix in ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139"]:
        number_type = "GSM"
    elif prefix in ["145", "146", "147", "148", "149"]:
        number_type = "Data Card"
    elif prefix in ["150", "151", "152", "153", "155", "156", "157", "158", "159"]:
        number_type = "GSM"
    elif prefix in ["166", "167", "168"]:
        number_type = "GSM"
    elif prefix in ["170", "171", "172", "173", "174", "175", "176", "177", "178"]:
        number_type = "Virtual"
    elif prefix in [
        "180",
        "181",
        "182",
        "183",
        "184",
        "185",
        "186",
        "187",
        "188",
        "189",
    ]:
        number_type = "GSM"
    elif prefix in ["198", "199"]:
        number_type = "GSM"
    else:
        number_type = "Unknown"

    return {
        "phone_number": phone_number,
        "clean_number": clean_number,
        "carrier": carrier,
        "number_type": number_type,
        "prefix": prefix,
        "is_valid": True,
    }


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """列出可用的工具"""
    return ListToolsResult(
        tools=[
            Tool(
                name="detect_carrier",
                description="检测手机号码的运营商信息，支持中国三大运营商（移动、联通、电信）和虚拟运营商的识别",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "要检测的手机号码，支持带格式的号码如 138-1234-5678 或纯数字 13812345678",
                        }
                    },
                    "required": ["phone_number"],
                },
            ),
            Tool(
                name="batch_detect_carriers",
                description="批量检测多个手机号码的运营商信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "phone_numbers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "要检测的手机号码列表",
                        }
                    },
                    "required": ["phone_numbers"],
                },
            ),
        ]
    )


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """处理工具调用"""

    if name == "detect_carrier":
        phone_number = arguments.get("phone_number")
        if not phone_number:
            return CallToolResult(
                content=[TextContent(type="text", text="错误：请提供手机号码")]
            )

        result = detect_carrier(phone_number)

        if "error" in result:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"检测失败：{result['error']} - {result['message']}",
                    )
                ]
            )

        # 格式化输出
        output = f"""📱 手机号码运营商检测结果

📞 号码：{result['phone_number']}
🏢 运营商：{result['carrier']}
📋 号码类型：{result['number_type']}
🔢 前缀：{result['prefix']}
✅ 状态：有效号码

---
*数据来源：中国三大运营商号码段数据库*"""

        return CallToolResult(content=[TextContent(type="text", text=output)])

    elif name == "batch_detect_carriers":
        phone_numbers = arguments.get("phone_numbers", [])
        if not phone_numbers:
            return CallToolResult(
                content=[TextContent(type="text", text="错误：请提供手机号码列表")]
            )

        results = []
        for phone in phone_numbers:
            result = detect_carrier(phone)
            results.append(result)

        # 格式化批量输出
        output = "📱 批量手机号码运营商检测结果\n\n"

        for i, result in enumerate(results, 1):
            if "error" in result:
                output += f"{i}. 📞 {result.get('phone_number', 'N/A')} - ❌ {result['error']}\n"
            else:
                output += f"{i}. 📞 {result['phone_number']} - 🏢 {result['carrier']} ({result['number_type']})\n"

        output += "\n---\n*数据来源：中国三大运营商号码段数据库*"

        return CallToolResult(content=[TextContent(type="text", text=output)])

    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"未知工具：{name}")]
        )


async def main():
    """主函数"""
    # 运行MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="phone-carrier-detector",
                server_version="1.0.0",
                capabilities={},
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
