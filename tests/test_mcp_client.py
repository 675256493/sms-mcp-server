#!/usr/bin/env python3
"""
简单的测试脚本，用于测试 MCP server 的功能
"""

from mcp_server import detect_carrier

# 测试单个号码
print("=== 测试单个号码 ===")
test_numbers = [
    "13812345678",  # 中国移动
    "13012345678",  # 中国联通
    "13312345678",  # 中国电信
    "17012345678",  # 虚拟运营商
    "99912345678",  # 未知运营商
    "138-1234-5678",  # 带格式的号码
    "1234567890",  # 无效号码
]

for number in test_numbers:
    result = detect_carrier(number)
    print(f"\n号码: {number}")
    print(f"结果: {result}")

# 测试批量检测
print("\n\n=== 测试批量检测 ===")
batch_numbers = ["13812345678", "13012345678", "13312345678"]
print(f"批量号码: {batch_numbers}")
results = [detect_carrier(num) for num in batch_numbers]
for i, result in enumerate(results, 1):
    print(f"{i}. {result['phone_number']} -> {result['carrier']}")
