#!/usr/bin/env python3
"""
测试运行脚本
"""

import sys
import os
import unittest
import argparse

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """运行所有测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_test(test_name):
    """运行指定的测试"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern=f"{test_name}.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    return run_specific_test("test_mcp_server")


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    return run_specific_test("test_mcp_integration")


def run_data_parser_tests():
    """运行数据解析器测试"""
    print("📊 运行数据解析器测试...")
    return run_specific_test("test_data_parser")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行 MCP Server 测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--data", action="store_true", help="运行数据解析器测试")
    parser.add_argument("--test", type=str, help="运行指定的测试文件")

    args = parser.parse_args()

    success = True

    if args.all:
        print("🚀 运行所有测试...")
        success = run_all_tests()
    elif args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.data:
        success = run_data_parser_tests()
    elif args.test:
        print(f"🎯 运行指定测试: {args.test}")
        success = run_specific_test(args.test)
    else:
        # 默认运行所有测试
        print("🚀 运行所有测试...")
        success = run_all_tests()

    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
