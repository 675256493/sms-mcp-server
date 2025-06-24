#!/usr/bin/env python3
"""
测试 MCP Server 启动和基本功能
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any


async def test_server_startup():
    """测试服务器启动"""
    print("🚀 测试 MCP Server 启动...")

    # 启动服务器
    process = await asyncio.create_subprocess_exec(
        "python",
        "mcp_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    print(f"✅ 服务器进程已启动 (PID: {process.pid})")

    # 等待一下确保服务器完全启动
    await asyncio.sleep(1)

    # 检查进程是否还在运行
    if process.returncode is None:
        print("✅ 服务器正在运行")
    else:
        print(f"❌ 服务器已退出，返回码: {process.returncode}")
        return False

    # 发送初始化请求
    init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

    request_line = json.dumps(init_request) + "\n"
    process.stdin.write(request_line.encode())
    await process.stdin.drain()

    # 读取响应
    try:
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if response_line:
            response = json.loads(response_line.decode().strip())
            print("✅ 服务器响应初始化请求:")
            print(f"   - JSON-RPC: {response.get('jsonrpc')}")
            print(
                f"   - 服务器名称: {response.get('result', {}).get('serverInfo', {}).get('name')}"
            )
            print(
                f"   - 版本: {response.get('result', {}).get('serverInfo', {}).get('version')}"
            )
        else:
            print("❌ 服务器没有响应")
            return False
    except asyncio.TimeoutError:
        print("❌ 服务器响应超时")
        return False
    except Exception as e:
        print(f"❌ 读取响应时出错: {e}")
        return False

    # 发送工具列表请求
    tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    request_line = json.dumps(tools_request) + "\n"
    process.stdin.write(request_line.encode())
    await process.stdin.drain()

    # 读取工具列表响应
    try:
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if response_line:
            response = json.loads(response_line.decode().strip())
            tools = response.get("result", {}).get("tools", [])
            print(f"✅ 服务器提供 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ 服务器没有响应工具列表请求")
            return False
    except Exception as e:
        print(f"❌ 读取工具列表响应时出错: {e}")
        return False

    # 测试工具调用
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "detect_carrier",
            "arguments": {"phone_number": "13812345678"},
        },
    }

    request_line = json.dumps(call_request) + "\n"
    process.stdin.write(request_line.encode())
    await process.stdin.drain()

    # 读取工具调用响应
    try:
        response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if response_line:
            response = json.loads(response_line.decode().strip())
            print(response)
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                data = json.loads(content)
                if data.get("success"):
                    print("✅ 工具调用成功:")
                    print(f"   - 手机号: {data['phone_number']}")
                    print(f"   - 运营商: {data['carrier']}")
                    print(f"   - 归属地: {data['province']} {data['city']}")
                else:
                    print(f"❌ 工具调用失败: {data.get('error')}")
            else:
                print(f"❌ 工具调用响应错误: {response}")
        else:
            print("❌ 服务器没有响应工具调用请求")
            return False
    except Exception as e:
        print(f"❌ 读取工具调用响应时出错: {e}")
        return False

    # 关闭服务器
    process.terminate()
    await process.wait()
    print("🛑 服务器已关闭")

    return True


def main():
    """主函数"""
    print("=" * 50)
    print("MCP Server 启动测试")
    print("=" * 50)

    try:
        success = asyncio.run(test_server_startup())
        if success:
            print("\n🎉 所有测试通过！MCP Server 启动成功！")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！MCP Server 有问题。")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
